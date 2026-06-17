#!/usr/bin/env bash
# =============================================================================
# reproduce.sh — one-shot, deterministic rebuild of the February deliverables
# =============================================================================
# Running this script reproduces BOTH verified outputs, with no LLM/API key:
#
#   1. outputs/Feb_summary.xlsx          (the Excel summary dashboard)
#   2. outputs/Feb_Report_final.pptx     (the PPT, slides 9,10,12,13,14,15 updated)
#
# It is fully deterministic — same inputs in data/ + the pinned base deck always
# produce the same outputs. The two steps are:
#
#   STEP 1  build_feb_summary.py   feb_basic + jan_summary(template) -> Feb_summary.xlsx
#   STEP 2  update_slides_9_15.py  base deck + Feb_summary.xlsx + jan refs -> final PPT
#
# The base deck (outputs/Feb_Report_20260614.pptx) is a pinned input artifact: it
# carries all upstream work for slides 16+ and the chart scaffolding. Step 2
# rewrites slides 9,10,12,13,14,15 from data and leaves the rest untouched.
#
# Usage:
#   chmod +x reproduce.sh
#   ./reproduce.sh                 # produce both outputs
#   ./reproduce.sh --validate      # also rebuild Jan summary and diff vs the real one
#
# Optional overrides (env vars):
#   BASE_DECK=outputs/Feb_Report_20260614.pptx   OUT_PPT=outputs/Feb_Report_final.pptx
# =============================================================================

set -euo pipefail

# Always run from the directory this script lives in (repo root).
cd "$(dirname "$0")"

# ── colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; CYAN='\033[0;36m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
log()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()     { echo -e "${GREEN}[OK]${NC}    $*"; }
error()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }
header() { echo -e "\n${BOLD}$*${NC}"; printf '%.0s─' {1..60}; echo; }

# ── configuration ──────────────────────────────────────────────────────────────
VENV_DIR=".venv"
OUTPUT_DIR="outputs"
FEB_SUMMARY="$OUTPUT_DIR/Feb_summary.xlsx"
BASE_DECK="${BASE_DECK:-$OUTPUT_DIR/Feb_Report_20260614.pptx}"
OUT_PPT="${OUT_PPT:-$OUTPUT_DIR/Feb_Report_final.pptx}"

VALIDATE=""
[ "${1:-}" = "--validate" ] && VALIDATE="1"

# ── step 0: pre-flight ───────────────────────────────────────────────────────
header "STEP 0 — Pre-flight checks"

PYTHON=$(command -v python3 || command -v python || true)
[ -z "$PYTHON" ] && error "Python 3 not found. Install from https://python.org"
ok "Python: $($PYTHON --version 2>&1)"

# Every input the two deterministic steps need.
REQUIRED=(
  "build_feb_summary.py"
  "update_slides_9_15.py"
  "relabel_charts.py"
  "data/jan_summary.xlsx"
  "data/jan_report.pptx"
  "data/feb_basic/MOHAP CSAT Tabs - Feb 2026.xlsx"
  "data/jan_basic/MOHAP CSAT Tabs for Jan-2026.xlsx"
  "$BASE_DECK"
)
for p in "${REQUIRED[@]}"; do
  [ -e "$p" ] || error "Required input missing: $p"
done
ok "All ${#REQUIRED[@]} required inputs present"

# ── step 1: virtual environment + deps ───────────────────────────────────────
header "STEP 1 — Python environment"

if [ ! -d "$VENV_DIR" ]; then
  log "Creating virtual environment in $VENV_DIR ..."
  $PYTHON -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
PY="$VENV_DIR/bin/python"

# The deterministic pipeline only needs these two packages (lxml ships with pptx).
log "Installing openpyxl + python-pptx ..."
pip install --upgrade pip --quiet
pip install --quiet "openpyxl>=3.1.0" "python-pptx>=0.6.23"
ok "Dependencies ready"

mkdir -p "$OUTPUT_DIR"

# ── optional: validate the summary builder against the real Jan summary ───────
if [ -n "$VALIDATE" ]; then
  header "STEP 1b — Validate summary logic (rebuild Jan, diff vs real)"
  $PY build_feb_summary.py --validate
fi

# ── step 2: build the Excel summary ──────────────────────────────────────────
header "STEP 2 — Build Excel summary"
$PY build_feb_summary.py --out "$FEB_SUMMARY"
[ -f "$FEB_SUMMARY" ] || error "Summary not produced: $FEB_SUMMARY"
ok "Wrote $FEB_SUMMARY"

# ── step 3: build the PPT (uses the summary from step 2) ──────────────────────
header "STEP 3 — Build PPT (slides 9,10,12,13,14,15)"
$PY update_slides_9_15.py "$BASE_DECK" "$OUT_PPT" --feb-summary "$FEB_SUMMARY"
[ -f "$OUT_PPT" ] || error "PPT not produced: $OUT_PPT"
ok "Wrote $OUT_PPT"

# ── done ─────────────────────────────────────────────────────────────────────
header "DONE"
ok "Excel summary : $FEB_SUMMARY"
ok "PowerPoint    : $OUT_PPT"
echo -e "\n${BOLD}Verify:${NC} open both files; the PPT audit is at ${OUT_PPT%.pptx}_audit.json"
