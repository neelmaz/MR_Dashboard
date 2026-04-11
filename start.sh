#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Start the FastAPI app on a free available port.
# Uvicorn will bind to an OS-assigned port and print the URL it is listening on.
.venv/bin/python -m uvicorn app:app --reload --port 0
