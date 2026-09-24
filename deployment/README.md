# BIO103 homelab deployment

The app uses a three-stage Node 24 Alpine image and Next.js standalone output. The final image contains the server and public learning assets. It runs as UID 1001 with a read-only filesystem, no added Linux capabilities, a bounded writable cache, and a health check at `/api/health`. Learning progress remains in each browser's local storage.

## Target

- Existing CasaOS server: `tahsinulmohsin@192.168.31.10` (`tahsin-server`, Linux x86_64).
- Container/image: `bio103-fieldnotes`.
- Proposed public hostname: `bio103.giggly.store.cv`.
- Private origin: Docker network `bio103-ingress`, container port `3000`.
- Host loopback health endpoint: `http://127.0.0.1:3103/api/health`.
- Route: Cloudflare HTTPS → existing Cloudflare Tunnel → Nginx Proxy Manager → app.

The existing Cloudflare credential is scoped to `giggly.store.cv`. Existing tunnel hostnames and Nginx Proxy Manager routes must remain intact. No Cloudflare token, private key, database password, or account credential belongs in this repository.

## Build and start on the server

Run in the copied application directory after installing its source and assets:

```sh
docker network inspect bio103-ingress >/dev/null 2>&1 || docker network create bio103-ingress
docker compose build --pull
docker compose up -d --wait
docker network connect bio103-ingress nginxproxymanager
curl --fail http://127.0.0.1:3103/api/health
```

For repeat deployments, first check whether `nginxproxymanager` already belongs to `bio103-ingress` and skip the connect command when it does. Keep `output: 'standalone'` in the Next.js configuration.

## Nginx Proxy Manager and Cloudflare

The included routing scripts default to a dry-run. Run them on the server from this application's source directory:

```sh
python3 deployment/configure-nginx.py
python3 deployment/configure-cloudflare.py
python3 deployment/configure-nginx.py --apply
python3 deployment/configure-cloudflare.py --apply
```

The Nginx script installs `nginx-bio103.conf` using NPM's [documented custom HTTP configuration include](https://nginxproxymanager.com/advanced-config/#custom-nginx-configurations), validates with `nginx -t`, and gracefully reloads. This custom host is maintained by this file rather than the NPM proxy-host editor. It does not edit the NPM database or existing hosts. It also persists `bio103-ingress` in the CasaOS NPM Compose file so future NPM recreation retains access to the app; the current NPM container is connected without a restart. The existing `network_mode: bridge` is replaced by the named Docker network, preserving ports, volumes, environment, and CasaOS metadata.

The Cloudflare script adds only `bio103.giggly.store.cv` to the existing tunnel, forwarding to Nginx Proxy Manager at `http://192.168.31.10:80`. It retains the catch-all `http_status:404` rule last and preserves unrelated rules. Both scripts store restricted backups under `deployment/private/` on the server and avoid printing credentials.

Create a proxied CNAME in the existing zone pointing to the existing tunnel. Public TLS terminates at Cloudflare and the tunnel encrypts transit to the homelab; the last hop is inside the host's Docker network. Validate the public HTTPS endpoint and confirm plain HTTP redirects to HTTPS. Use a hostname-specific Cloudflare redirect or Nginx rule that checks `X-Forwarded-Proto` when needed; a blanket origin HTTP-to-HTTPS redirect can loop behind the tunnel.

## Verification

```sh
docker compose ps
docker inspect bio103-fieldnotes --format '{{.State.Health.Status}}'
curl --fail http://127.0.0.1:3103/api/health
curl --fail -H 'Host: bio103.giggly.store.cv' http://127.0.0.1/api/health
curl --fail https://bio103.giggly.store.cv/api/health
```

Open the public site and test the explanation → recall → quiz flow. Container restart must not erase progress already saved in the same browser. No database is required.

## Rollback

Tag the previous image before replacing it and retain the prior tunnel configuration and app-specific Nginx route. To roll back the application, set `BIO103_IMAGE_TAG` to the retained image tag and run `docker compose up -d --wait`. To remove this deployment, stop only this Compose project, remove only its proxy route and tunnel hostname, and delete only its DNS record. Never prune all containers, networks, images, or Cloudflare routes.

## Status

Deployment discovery completed. Live deployment verification will be recorded after the app passes its local QA and the container is built on the server.
