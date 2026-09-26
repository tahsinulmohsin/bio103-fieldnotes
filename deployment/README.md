# Deployment

Production: **https://fieldnotes.tahsinulmohsin.me**. `GET /api/health` returns `{"status":"ok","app":"bio103-fieldnotes","version":"…"}`.

The app ships as a three-stage Node 24 Alpine image with Next.js standalone output. The final image contains the server, the prerendered lecture data and the public learning assets. `compose.yaml` runs it:
- as UID 1001, with a read-only root filesystem, all Linux capabilities dropped and `no-new-privileges`;
- with tmpfs mounts for `/tmp` and the Next.js cache;
- with a health check at `/api/health`.

Learning progress stays in each browser's local storage, so no database is needed.

## At a glance

| | |
|---|---|
| Public URL | https://fieldnotes.tahsinulmohsin.me (Cloudflare in front; TLS terminates there) |
| Container / image | `bio103-fieldnotes-app` / `bio103-fieldnotes:latest` |
| Ports | host `3103` → container `3000` |
| Health | `/api/health` (status, app, version) |
| Rollback image | `bio103-fieldnotes:previous` |

No server address, Cloudflare token, tunnel ID, private key or account credential belongs in this repository. Server settings live in `.deploy.env`, which is not committed. The proxy scripts take the tunnel ID and origin as arguments.

## Deploy from your computer

Copy `.deploy.env.example` to `.deploy.env` and set `DEPLOY_HOST` and `DEPLOY_USER`. You can also set `DEPLOY_DIR`, `DEPLOY_SSH_KEY`, `DEPLOY_PORT`, `PUBLIC_URL`, and `DEPLOY_PROXY_NETWORK=1` for the proxy route below. Then run:

```sh
./deploy.sh
```

It does five things:
1. Rsyncs the project to the server, skipping `node_modules`, `.next`, `.git`, caches, `.deploy.env` and the proxy scripts' backups in `deployment/private/`.
2. Tags the running image `bio103-fieldnotes:previous`.
3. Builds the new image while the old container keeps serving.
4. Recreates the container.
5. Waits for `/api/health` to return 200, then prints the reported version.

## Build and start on the server manually

In the copied project directory:

```sh
docker compose build --pull
docker compose up -d --wait
curl --fail http://127.0.0.1:3103/api/health
```

Keep `output: 'standalone'` in the Next.js configuration (it is set whenever the build is not on Vercel).

## Optional: Nginx Proxy Manager and a Cloudflare Tunnel

`deployment/` has scripts that route the hostname through a Cloudflare Tunnel to Nginx Proxy Manager, then to the app over a shared Docker network. They are only needed if you run that route; the site works without them.

The route uses these pieces:
- `compose.proxy.yaml`: a Compose override. It joins the app to the external `bio103-ingress` network under the alias `bio103-fieldnotes`.
- `nginx-bio103.conf`: an Nginx server for `fieldnotes.tahsinulmohsin.me` that proxies to `bio103-fieldnotes:3000` on that network.
- `configure-nginx.py`: installs that server in Nginx Proxy Manager.
- `configure-cloudflare.py`: adds the hostname to the tunnel.

**1. Put the app on the shared network.** Set `DEPLOY_PROXY_NETWORK=1` in `.deploy.env` and run `./deploy.sh`. It creates `bio103-ingress` if needed and deploys with the override. By hand on the server:

```sh
docker network inspect bio103-ingress >/dev/null 2>&1 || docker network create bio103-ingress
COMPOSE_FILE=compose.yaml:deployment/compose.proxy.yaml docker compose up -d --wait
```

Keep the override for every later deploy and rollback, or the app leaves the network and the route stops working.

**2. Dry-run, then apply**, on the server from the project directory:

```sh
python3 deployment/configure-nginx.py
python3 deployment/configure-cloudflare.py --tunnel-id <tunnel-id> --origin http://<server>:80
python3 deployment/configure-nginx.py --apply
python3 deployment/configure-cloudflare.py --tunnel-id <tunnel-id> --origin http://<server>:80 --apply
```

Both scripts dry-run by default, never print credentials, and keep private backups in `deployment/private/`. `deploy.sh` leaves that folder alone on the server.

**What `configure-nginx.py` does:**
- Checks that `bio103-fieldnotes-app` is healthy and on `bio103-ingress` as `bio103-fieldnotes`. It stops if not, and the dry-run says what is missing.
- Installs `nginx-bio103.conf` through Nginx Proxy Manager's [custom HTTP configuration include](https://nginxproxymanager.com/advanced-config/#custom-nginx-configurations).
- Connects NPM to `bio103-ingress`, validates with `nginx -t`, reloads, and checks `/api/health` through NPM.
- Only then records the network in NPM's Compose file, so a recreated NPM keeps the route. The NPM database and other hosts are not touched.
- If any step fails, it restores the previous configuration.

**What `configure-cloudflare.py` does:**
- Adds only this hostname (`--hostname`, default `fieldnotes.tahsinulmohsin.me`) to the tunnel, just before the catch-all `http_status:404` rule, and creates its proxied CNAME to `<tunnel-id>.cfargotunnel.com`.
- Leaves unrelated rules alone and only works inside the zone of the cloudflared certificate (`~/.cloudflared/cert.pem`, or `--certificate`).
- Refuses to replace a hostname that already routes somewhere else or has a different DNS record, so running it against a hostname that already works changes nothing.
- If the DNS step fails, it removes the route it added.

Behind a tunnel, check `X-Forwarded-Proto` for the HTTP → HTTPS redirect, as `nginx-bio103.conf` does. A blanket origin redirect can loop.

## Verification

```sh
docker compose ps
docker inspect bio103-fieldnotes-app --format '{{.State.Health.Status}}'
curl --fail http://127.0.0.1:3103/api/health
curl --fail https://fieldnotes.tahsinulmohsin.me/api/health
```

Open the site and walk through Read → Recall → Practise. Restarting the container must not erase progress already saved in the same browser.

## Rollback

`deploy.sh` keeps the image it replaces as `bio103-fieldnotes:previous`. To roll back, run this in the project directory on the server:

```sh
BIO103_IMAGE_TAG=previous docker compose up -d --wait
```

If the app is on the proxy network, include the override: `COMPOSE_FILE=compose.yaml:deployment/compose.proxy.yaml BIO103_IMAGE_TAG=previous docker compose up -d --wait`.

To remove the deployment, stop only this Compose project, remove only its proxy route and tunnel hostname, and delete only its DNS record. Never prune all containers, networks, images or Cloudflare routes.

## Access

The site is public, and it serves the original lecture files to anyone who can reach it. If it should be limited to NSU students, put the hostname behind a Cloudflare Access policy.
