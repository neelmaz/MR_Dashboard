#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v ngrok >/dev/null 2>&1; then
  cat <<'EOF'
ngrok is not installed.
Install it from https://ngrok.com/download and add it to your PATH.
If you have an ngrok authtoken, run:
  ngrok config add-authtoken YOUR_AUTHTOKEN
EOF
  exit 1
fi

ngrok_version=$(ngrok version 2>/dev/null | awk '{print $3}' | tr -d '\n')
if [[ -z "$ngrok_version" ]]; then
  echo "Unable to determine ngrok version. Please install ngrok 3.20.0 or newer."
  exit 1
fi

required_version="3.20.0"
version_lt() {
  local a b
  IFS='.' read -r -a a <<< "$1"
  IFS='.' read -r -a b <<< "$2"
  for i in 0 1 2; do
    if [[ -z "${a[i]}" ]]; then a[i]=0; fi
    if [[ -z "${b[i]}" ]]; then b[i]=0; fi
    if (( a[i] < b[i] )); then
      return 0
    elif (( a[i] > b[i] )); then
      return 1
    fi
  done
  return 1
}

if version_lt "$ngrok_version" "$required_version"; then
  cat <<'EOF'
Your ngrok agent is too old: version $ngrok_version.
The minimum supported version for your account is $required_version.
Update ngrok with one of the following commands:
  ngrok update
  brew upgrade ngrok
or download the latest version from https://ngrok.com/download
EOF
  exit 1
fi

mkdir -p certs
if [[ ! -f certs/server.key || ! -f certs/server.crt ]]; then
  echo "Generating self-signed certificate..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certs/server.key \
    -out certs/server.crt \
    -subj "/C=US/ST=State/L=City/O=Localhost/CN=localhost"
fi

if ! lsof -iTCP:8443 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Starting local HTTPS server on port 8443..."
  .venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8443 \
    --ssl-keyfile certs/server.key --ssl-certfile certs/server.crt > /tmp/ngrok_server.log 2>&1 &
  server_pid=$!
  trap 'echo "Stopping local HTTPS server..."; kill "$server_pid" 2>/dev/null || true' EXIT
  sleep 2
else
  echo "Local HTTPS server already running on port 8443."
fi

echo "Starting ngrok tunnel to https://127.0.0.1:8443"
ngrok http https://127.0.0.1:8443
