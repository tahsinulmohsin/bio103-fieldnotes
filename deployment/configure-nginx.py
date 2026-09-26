#!/usr/bin/env python3
"""Install the isolated BIO103 host in the existing Nginx Proxy Manager.

Run on the server that runs Nginx Proxy Manager. Dry-run is the default. Existing NPM configuration is
backed up privately, validated, and restored if installation fails. Other proxy
hosts are not edited. The existing NPM container is gracefully reloaded.
"""

import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

NPM = "nginxproxymanager"
HOSTNAME = "fieldnotes.tahsinulmohsin.me"  # must match server_name in nginx-bio103.conf
NETWORK = "bio103-ingress"
CASA_DIR = "/var/lib/casaos/apps/nginxproxymanager"
HTTP_CONFIG = "/data/nginx/custom/http.conf"
APP_CONFIG = "/data/nginx/custom/bio103.conf"
INCLUDE = "include /data/nginx/custom/bio103.conf;"


def run(command, text=None):
    result = subprocess.run(command, input=text, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {command[0]} {command[1]}")
    return result.stdout


def read_npm(path):
    result = subprocess.run(["docker", "exec", NPM, "cat", path], text=True, capture_output=True)
    return result.stdout if result.returncode == 0 else None


def write_npm(path, contents):
    if contents is None:
        run(["docker", "exec", NPM, "rm", "-f", path])
    else:
        run(["docker", "exec", "-i", NPM, "sh", "-c", "mkdir -p /data/nginx/custom && cat > " + path + ".bio103.tmp && mv " + path + ".bio103.tmp " + path], contents)


def casa_file(contents=None):
    command = ["docker", "run", "--rm", "-i", "--network", "none", "--read-only", "--mount", "type=bind,src=" + CASA_DIR + ",dst=/config" + (",readonly" if contents is None else ""), "python:3.12-slim", "python", "-c"]
    if contents is None:
        return run(command + ["from pathlib import Path; print(Path('/config/docker-compose.yml').read_text(),end='')"])
    run(command + ["""from pathlib import Path
import os, stat, sys, tempfile
destination = Path('/config/docker-compose.yml')
metadata = destination.stat()
temporary = None
try:
    with tempfile.NamedTemporaryFile(mode='w', dir='/config', prefix='.bio103-', delete=False) as output:
        temporary = Path(output.name)
        os.chmod(temporary, stat.S_IMODE(metadata.st_mode))
        os.chown(temporary, metadata.st_uid, metadata.st_gid)
        output.write(sys.stdin.read())
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(destination)
finally:
    if temporary and temporary.exists():
        temporary.unlink()
"""], contents)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    desired = (base / "nginx-bio103.conf").read_text()
    existing_http = read_npm(HTTP_CONFIG)
    existing_app = read_npm(APP_CONFIG)
    original_casa = casa_file()
    updated_casa = original_casa
    if "        network_mode: bridge\n" in original_casa:
        if original_casa.count("        network_mode: bridge\n") != 1 or original_casa.count("\nnetworks:\n") != 1:
            raise RuntimeError("Unexpected CasaOS network structure; refusing a broad edit")
        updated_casa = original_casa.replace("        network_mode: bridge\n", "        networks:\n            - bio103-ingress\n", 1)
        updated_casa = updated_casa.replace("\nnetworks:\n", "\nnetworks:\n    bio103-ingress:\n        external: true\n        name: bio103-ingress\n", 1)
    elif "            - bio103-ingress\n" not in original_casa or "    bio103-ingress:\n" not in original_casa:
        raise RuntimeError("Unexpected CasaOS network structure; inspect before applying")
    if existing_app is not None and existing_app != desired:
        raise RuntimeError("An unexpected BIO103 Nginx file exists; inspect before replacing it")
    updated_http = existing_http or ""
    if INCLUDE not in updated_http.splitlines():
        updated_http = updated_http.rstrip() + "\n" + INCLUDE + "\n"
    npm_state = json.loads(run(["docker", "inspect", NPM]))[0]
    already_connected = NETWORK in npm_state["NetworkSettings"]["Networks"]
    print(json.dumps({"nginxHost": HOSTNAME, "network": NETWORK, "connectNetwork": not already_connected, "persistCasaOsNetwork": original_casa != updated_casa, "existingProxyHostsEdited": False, "apply": args.apply}, indent=2))
    if not args.apply:
        return
    app_state = json.loads(run(["docker", "inspect", "bio103-fieldnotes"]))[0]
    if app_state["State"].get("Health", {}).get("Status") != "healthy":
        raise RuntimeError("BIO103 container must be healthy before routing it")
    os.umask(0o077)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = base / "private" / ("nginx-before-" + stamp)
    backup.mkdir(parents=True, mode=0o700)
    (backup / "casaos-compose.yaml").write_text(original_casa)
    (backup / "state.json").write_text(json.dumps({"httpConfig": existing_http, "appConfig": existing_app, "networkConnected": already_connected}, indent=2))
    validation_file = backup / "updated-casaos-compose.yaml"
    validation_file.write_text(updated_casa)
    run(["docker", "compose", "-f", str(validation_file), "config", "--quiet"])
    connected = False
    casa_changed = False
    try:
        if not already_connected:
            run(["docker", "network", "connect", NETWORK, NPM])
            connected = True
        write_npm(APP_CONFIG, desired)
        write_npm(HTTP_CONFIG, updated_http)
        run(["docker", "exec", NPM, "nginx", "-t"])
        run(["docker", "exec", NPM, "nginx", "-s", "reload"])
        request = urllib.request.Request("http://127.0.0.1/api/health", headers={"Host": HOSTNAME, "X-Forwarded-Proto": "https"})
        for attempt in range(20):
            try:
                with urllib.request.urlopen(request, timeout=5) as response:
                    if response.status == 200:
                        break
            except OSError:
                if attempt == 19:
                    raise RuntimeError("Nginx health request failed after reload") from None
            time.sleep(0.5)
        else:
            raise RuntimeError("Nginx health request failed after reload")
        if updated_casa != original_casa:
            if casa_file() != original_casa:
                raise RuntimeError("CasaOS configuration changed concurrently; retry after review")
            casa_file(updated_casa)
            casa_changed = True
        print("Nginx origin is healthy. Only the BIO103 route and its shared network were added; private backups saved.")
    except Exception:
        if casa_changed:
            casa_file(original_casa)
        write_npm(HTTP_CONFIG, existing_http)
        write_npm(APP_CONFIG, existing_app)
        run(["docker", "exec", NPM, "nginx", "-t"])
        run(["docker", "exec", NPM, "nginx", "-s", "reload"])
        if connected:
            run(["docker", "network", "disconnect", NETWORK, NPM])
        raise


if __name__ == "__main__":
    main()
