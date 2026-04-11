# Nissan Automotive Benchmark Dashboard

This project runs a FastAPI web dashboard backed by `nissan_dataset.csv`.

## Run locally

```bash
cd "/Users/neelanjanmazumder/Library/CloudStorage/OneDrive-Personal/Feedback_MR"
.venv/bin/python -m uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Run with HTTPS locally

```bash
chmod +x https_start.sh
./https_start.sh
```

Open:

```text
https://127.0.0.1:8443
```

This script generates a self-signed certificate in `certs/server.crt` / `certs/server.key`.

> Note: Browsers will show a warning for the self-signed certificate. For a trusted public URL, use a real certificate or a tunnel service.

## Share externally

To expose the local HTTPS server outside your network, use one of these options:

1. Use `ngrok` or Cloudflare Tunnel.
2. Open and forward port `8443` on your router/firewall.
3. Use a hosted deployment with HTTPS support.

### Example using `ngrok`

```bash
ngrok http https://127.0.0.1:8443
```

> If you see an error like `authentication failed: Your ngrok-agent version "3.3.1" is too old`, update ngrok to version `3.20.0` or newer with `ngrok update`, `brew upgrade ngrok`, or by downloading from https://ngrok.com/download.

## One-step ngrok tunnel

```bash
chmod +x ngrok_start.sh
./ngrok_start.sh
```

If you want a stable public tunnel, configure your ngrok auth token first:

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

This script ensures the local HTTPS server is running and then launches an ngrok tunnel to it.

Then share the `https://...ngrok.io` URL.

## Deploy from GitHub to Render

The repository is ready to deploy from GitHub using Docker.

1. Go to https://render.com and connect your GitHub account.
2. Create a new Web Service and select the `neelmaz/MR_Dashboard` repo.
3. Render will detect `render.yaml` and use the `Dockerfile` automatically.
4. Once deployed, Render will give you a public HTTPS URL.

This is the best way to make the FastAPI dashboard accessible outside without running ngrok manually.
