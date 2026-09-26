# BIO103 homelab deployment

The app uses a three-stage Node 24 Alpine image and Next.js standalone output. The final image contains the server, the prerendered topic data and the public learning assets. `compose.yaml` runs it as UID 1001 with a read-only root filesystem, all Linux capabilities dropped, `no-new-privileges`, tmpfs mounts for `/tmp` and the Next.js cache, and a health check at `/api/health`. Learning progress stays in each browser's local storage.

## Target

- Existing CasaOS server: `tahsinulmohsin@192.168.31.10` (`tahsin-server`, Linux x86_64).
- Container/image: `bio103-fieldnotes`.
- Proposed public hostname: `bio103.giggly.store.cv`.
- Private origin: Docker network `bio103-ingress`, container port `3000`.
- LAN address: `http://192.168.31.10:3103/` (Compose publishes port 3103 on all interfaces).
- Health endpoint: `http://192.168.31.10:3103/api/health`.
- Route: Cloudflare HTTPS → existing Cloudflare Tunnel → Nginx Proxy Manager → app.

The existing Cloudflare credential is scoped to `giggly.store.cv`. Existing tunnel hostnames and Nginx Proxy Manager routes must remain intact. No Cloudflare token, private key, database password, or account credential belongs in this repository.

## Deploy from this computer

`./deploy.sh` rsyncs this folder to `~/bio103` on the server (skipping `node_modules`, `.next`, `.cache` and similar), tags the running image as `bio103-fieldnotes:previous`, builds the new image while the old container keeps serving, recreates the container and waits for `/api/health` to return 200.

## Build and start on the server manually

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

`deploy.sh` keeps the image it replaces as `bio103-fieldnotes:previous`. To roll back, run `BIO103_IMAGE_TAG=previous docker compose up -d --wait` in `~/bio103` on the server. To remove this deployment, stop only this Compose project, remove only its proxy route and tunnel hostname, and delete only its DNS record. Never prune all containers, networks, images, or Cloudflare routes.

## Status

The container runs on the homelab and is reachable on the LAN at port 3103. The public route (Nginx Proxy Manager host and Cloudflare tunnel hostname for `bio103.giggly.store.cv`) has not been applied; the hostname does not resolve. Apply it with the scripts above only if the app should be reachable from the internet, and consider a Cloudflare Access policy first, since the original lecture files are served to anyone who can reach the app.
