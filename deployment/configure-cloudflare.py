#!/usr/bin/env python3
"""Add only this app's DNS record and ingress rule using the server's certificate.

Dry-run is the default. Credentials are read into memory and are never printed.
Run this on the server that runs cloudflared, after verifying the Nginx origin.
"""

import argparse
import base64
import copy
import datetime
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hostname", default="fieldnotes.tahsinulmohsin.me")
    parser.add_argument("--tunnel-id", required=True, help="ID of the existing Cloudflare Tunnel")
    parser.add_argument("--origin", required=True, help="where the tunnel forwards, e.g. http://<server>:80 (Nginx Proxy Manager)")
    parser.add_argument("--certificate", type=Path, default=Path.home() / ".cloudflared/cert.pem")
    parser.add_argument("--backup-dir", type=Path, default=Path(__file__).parent / "private")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]+[a-z0-9]", args.hostname):
        raise SystemExit("Invalid hostname")

    certificate = json.loads(base64.b64decode(re.sub(r"-----[^-]+-----|\s", "", args.certificate.read_text())))

    def api(path, method="GET", body=None):
        request = urllib.request.Request(
            "https://api.cloudflare.com/client/v4" + path,
            data=None if body is None else json.dumps(body).encode(),
            method=method,
            headers={"Authorization": "Bearer " + certificate["apiToken"], "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            # Never print the request object or its Authorization header.
            raise RuntimeError(f"Cloudflare {method} failed with HTTP {error.code}") from None
        if not result.get("success"):
            raise RuntimeError(f"Cloudflare {method} did not succeed")
        return result.get("result")

    zone_path = "/zones/" + certificate["zoneID"]
    zone = api(zone_path)
    if not args.hostname.endswith("." + zone["name"]):
        raise SystemExit("Requested hostname is outside the existing certificate's zone")
    tunnel_path = "/accounts/" + certificate["accountID"] + "/cfd_tunnel/" + args.tunnel_id + "/configurations"
    current = api(tunnel_path)["config"]
    updated = copy.deepcopy(current)
    ingress = updated.setdefault("ingress", [])
    matching = [rule for rule in ingress if rule.get("hostname") == args.hostname]
    desired_rule = {"hostname": args.hostname, "service": args.origin}
    if matching and (len(matching) != 1 or matching[0].get("service") != args.origin):
        raise SystemExit("Hostname already has a different tunnel route; refusing to replace it")
    if not matching:
        fallback_index = next((index for index, rule in enumerate(ingress) if not rule.get("hostname")), len(ingress))
        ingress.insert(fallback_index, desired_rule)

    dns_path = zone_path + "/dns_records"
    records = api(dns_path + "?" + urllib.parse.urlencode({"name": args.hostname}))
    cname = args.tunnel_id + ".cfargotunnel.com"
    if records and (len(records) != 1 or records[0].get("type") != "CNAME" or records[0].get("content") != cname or not records[0].get("proxied")):
        raise SystemExit("Hostname already has a different DNS record; refusing to replace it")
    print(json.dumps({"hostname": args.hostname, "origin": args.origin, "existingRoutesPreserved": len(current.get("ingress", [])), "addRoute": not matching, "addDns": not records, "apply": args.apply}, indent=2))
    if not args.apply:
        return

    args.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(args.backup_dir, 0o700)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = args.backup_dir / ("cloudflare-before-" + stamp + ".json")
    descriptor = os.open(backup, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w") as output:
        json.dump({"hostname": args.hostname, "tunnelId": args.tunnel_id, "config": current, "dns": records}, output, indent=2)
    route_added = False
    created_dns_id = None
    try:
        if not matching:
            # Avoid overwriting a configuration changed during the preceding checks.
            if api(tunnel_path)["config"] != current:
                raise RuntimeError("Tunnel configuration changed concurrently; run again")
            api(tunnel_path, "PUT", {"config": updated})
            route_added = True
        if not records:
            created_dns_id = api(dns_path, "POST", {"type": "CNAME", "name": args.hostname, "content": cname, "proxied": True, "ttl": 1})["id"]
        result_config = api(tunnel_path)["config"]
        if not any(rule.get("hostname") == args.hostname and rule.get("service") == args.origin for rule in result_config.get("ingress", [])):
            raise RuntimeError("New ingress route was not retained")
        original_rules = [rule for rule in current.get("ingress", []) if rule.get("hostname") != args.hostname]
        preserved_rules = [rule for rule in result_config.get("ingress", []) if rule.get("hostname") != args.hostname]
        if original_rules != preserved_rules:
            raise RuntimeError("Unrelated ingress rules changed during deployment")
        print("Cloudflare route and proxied DNS configured; original configuration backed up on the server.")
    except Exception:
        if created_dns_id:
            api(dns_path + "/" + created_dns_id, "DELETE")
        if route_added:
            latest = api(tunnel_path)["config"]
            latest["ingress"] = [rule for rule in latest.get("ingress", []) if rule.get("hostname") != args.hostname]
            api(tunnel_path, "PUT", {"config": latest})
        raise


if __name__ == "__main__":
    main()
