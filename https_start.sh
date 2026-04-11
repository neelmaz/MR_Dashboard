#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p certs

if [[ ! -f certs/server.key || ! -f certs/server.crt ]]; then
  echo "Generating self-signed certificate..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certs/server.key \
    -out certs/server.crt \
    -subj "/C=US/ST=State/L=City/O=Localhost/CN=localhost"
fi

host_ip=$(python - <<'PY'
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(('8.8.8.8', 80))
    print(s.getsockname()[0])
finally:
    s.close()
PY
)

if [[ -z "$host_ip" ]]; then
  host_ip="127.0.0.1"
fi

echo "Starting FastAPI with HTTPS on https://0.0.0.0:8443"
echo "Open from another laptop on the same LAN via: https://$host_ip:8443"
.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8443 \
  --ssl-keyfile certs/server.key --ssl-certfile certs/server.crt
