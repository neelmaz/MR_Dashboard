# Monthly Report Generation Pipeline

An agentic LangGraph pipeline that learns mapping logic from January reference
files and automatically generates the February summary Excel and updated PPT.

## Architecture

```
Inputs (Feb basic tables + Jan reference files)
    │
    ▼
1. Ingestion Agent       — parses all Excel + PPT into state
    │
    ▼
2. Mapping Agent (LLM)   — infers Excel rules + PPT-to-cell mappings
    │
    ▼
3. Excel Generator       — builds Feb summary workbook
    │
    ▼
4. PPT Updater           — replaces Arabic text runs in Feb PPT
    │
    ▼
5. QA Agent (LLM)        — cross-validates outputs vs source data
    │
    ├─ FAIL (retry ≤2)   → back to Mapping Agent
    │
    ▼
6. Human Review Gate     — optional interactive approval
    │
    ▼
7. Output Packager       — saves .xlsx, .pptx, audit_log.json, qa_report.json
```

## Setup

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

## Running

```bash
python main.py \
  --feb-basic-dir  ./data/feb_basic/ \
  --jan-basic-dir  ./data/jan_basic/ \
  --jan-summary    ./data/jan_summary.xlsx \
  --jan-ppt        ./data/jan_report.pptx \
  --output-dir     ./outputs/ \
  --seed-mappings  ./seed_mappings_example.json
```

Add `--auto-approve` to skip the human review gate (useful for CI/CD runs).

## Deterministic reproduction (`reproduce.sh`)

`main.py` above is the **LLM-agent** pipeline. The verified February deliverables,
however, were finalised with deterministic, data-driven scripts (no LLM, no API
key). To regenerate the exact same Excel summary and PPT, run:

```bash
./reproduce.sh              # builds both outputs
./reproduce.sh --validate   # also rebuilds the Jan summary and diffs it vs the real one
```

It creates/reuses `.venv`, installs just `openpyxl` + `python-pptx`, then runs two
steps in order:

1. `build_feb_summary.py`  — `data/feb_basic` + `data/jan_summary.xlsx` (template) → `outputs/Feb_summary.xlsx`
2. `update_slides_9_15.py` — base deck + `Feb_summary.xlsx` + Jan references → `outputs/Feb_Report_final.pptx`
   (rewrites slides 9, 10, 12, 13, 14, 15 from data; leaves 16+ untouched)

The output is reproducible: the same inputs always produce an identical summary and
PPT (verified — the regenerated PPT audit is byte-identical to the signed-off deck).

**Pinned input:** `reproduce.sh` treats `outputs/Feb_Report_20260614.pptx` as a base
artifact. That deck holds all upstream work for slides 16+ and the chart scaffolding
(produced by the earlier agent chain whose intermediate decks are no longer kept).
Keep that file and the `data/` folder under version control. Override paths via the
`BASE_DECK` / `OUT_PPT` env vars if needed.

## File Layout

```
report_pipeline/
├── main.py                  # Entry point
├── pipeline.py              # LangGraph graph construction
├── state.py                 # Shared TypedDict state schema
├── requirements.txt
├── seed_mappings_example.json
│
├── agents/
│   ├── ingestion_agent.py   # Parses all input files
│   ├── mapping_agent.py     # LLM: infers Excel + PPT mapping rules
│   ├── excel_generator.py   # Builds Feb summary workbook
│   ├── ppt_updater.py       # Updates Arabic PPT text runs
│   ├── qa_agent.py          # Validates outputs
│   ├── human_review.py      # Interrupt gate
│   └── output_packager.py   # Saves artifacts to disk
│
└── tools/
    ├── llm_client.py         # Gemini API wrapper with retry
    ├── excel_serialiser.py   # Excel → LLM-readable text
    └── ppt_serialiser.py     # PPT shapes → LLM-readable text
```

## Key Design Decisions

### Arabic/RTL PPT Safety
Text replacement is done at the **run level** (`shape.text_frame.paragraphs[i].runs[j].text`)
rather than the paragraph level. This preserves bidirectional text layout, font properties
(size, colour, bold), and RTL direction markers that python-pptx stores internally.

### Mapping Rule Inference
The Mapping Agent runs two LLM passes:
1. **Excel pass**: Shows Jan basic tables + Jan summary side-by-side, asks Claude to
   reverse-engineer the formula for each summary cell.
2. **PPT pass**: Shows extracted Arabic shapes (with run-level text) + Jan summary
   values, asks Claude to match shapes to cells.

### Seed Mappings
For shapes the LLM is uncertain about (confidence < 0.7), you can provide manual
overrides in `seed_mappings_example.json`. The key format is
`"slide_index_shape_id_run_index"` → `"SheetName!CellRef"`. These are applied
after LLM inference with confidence=1.0.

### QA + Retry
After generation, the QA agent cross-validates every changed cell and shape.
If checks fail and retry_count < 2, the graph loops back to the Mapping Agent
with the QA error report added to state so the LLM can self-correct.

### Outputs
Every run produces timestamped files:
- `Feb_Summary_YYYYMMDD_HHMMSS.xlsx`
- `Feb_Report_YYYYMMDD_HHMMSS.pptx`
- `audit_log_*.json`        — every cell/shape changed, old→new value
- `qa_report_*.json`        — full QA results
- `inferred_mappings_*.json` — save mapping rules to use as seeds next month
- `pipeline_errors_*.txt`   — any errors encountered (if any)

## Tips for Best Results

1. **First run**: Use `inferred_mappings_*.json` from the output as the seed file
   for the next month. The LLM's rules improve as you refine the seed hints.

2. **Large files**: If Excel files have >100 rows per sheet, the serialiser truncates
   them. Adjust `MAX_ROWS_PER_SHEET` in `tools/excel_serialiser.py`.

3. **Multiple PPT text runs**: If a shape has several runs with different formatting,
   check the `run_index` in the inferred mappings. Use seed_mappings to correct
   any wrong run index assignments.

4. **Percentage format**: The PPT updater auto-detects whether the original text used
   Arabic-Indic numerals (٠١٢٣...) or Western numerals and matches the format.
