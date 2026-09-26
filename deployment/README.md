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

Copy `.deploy.env.example` to `.deploy.env` and set `DEPLOY_HOST` and `DEPLOY_USER`. You can also set `DEPLOY_DIR`, `DEPLOY_SSH_KEY`, `DEPLOY_PORT` and `PUBLIC_URL`. Then run:

```sh
./deploy.sh
```

It does five things:
1. Rsyncs the project to the server, skipping `node_modules`, `.next`, `.git`, caches and `.deploy.env`.
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

`deployment/` has scripts that route a hostname to the app: Cloudflare Tunnel → Nginx Proxy Manager → container. Both scripts dry-run by default, keep restricted backups under `deployment/private/` on the server, and never print credentials.

> **Before applying:** these scripts were written for an earlier route and have not been run against the current `compose.yaml`. Two things need fixing first:
> - `nginx-bio103.conf` forwards to `bio103-fieldnotes:3000` on the `bio103-ingress` network, but Compose does not attach the app to that network. Attach it with that alias.
> - `configure-nginx.py` inspects a container named `bio103-fieldnotes`, but Compose names it `bio103-fieldnotes-app`.
>
> The live hostname does not depend on these scripts.

Run them on the server from the project directory:

```sh
python3 deployment/configure-nginx.py
python3 deployment/configure-cloudflare.py --tunnel-id <tunnel-id> --origin http://<server>:80
python3 deployment/configure-nginx.py --apply
python3 deployment/configure-cloudflare.py --tunnel-id <tunnel-id> --origin http://<server>:80 --apply
```

**`configure-nginx.py`**
- Installs `nginx-bio103.conf` (server name `fieldnotes.tahsinulmohsin.me`) through Nginx Proxy Manager's [custom HTTP configuration include](https://nginxproxymanager.com/advanced-config/#custom-nginx-configurations).
- Validates with `nginx -t`, then reloads gracefully.
- Leaves the NPM database and other hosts untouched.
- Connects NPM to the `bio103-ingress` Docker network and records that network in NPM's Compose file, so a recreated NPM keeps access to the app.

**`configure-cloudflare.py`**
- Adds only this hostname to the existing tunnel (`--hostname`, default `fieldnotes.tahsinulmohsin.me`) and its proxied CNAME.
- Keeps the catch-all `http_status:404` rule last and leaves unrelated rules alone.
- Only works inside the zone of the cloudflared certificate (`~/.cloudflared/cert.pem`, or `--certificate`).
- Refuses to replace a hostname that already routes somewhere else, so it is safe to run against the live hostname.

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

To remove the deployment, stop only this Compose project, remove only its proxy route and tunnel hostname, and delete only its DNS record. Never prune all containers, networks, images or Cloudflare routes.

## Access

The site is public, and it serves the original lecture files to anyone who can reach it. If it should be limited to NSU students, put the hostname behind a Cloudflare Access policy.
