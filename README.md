# OTB Planner — Open-to-Buy Data Entry UI

A Streamlit web app for editing `OTB_v2.xlsx` without touching Excel.

---

## Setup (3 steps)

```bash
# 1 — Install dependencies
pip install -r requirements.txt

# 2 — Run the app (from the otb_app directory)
streamlit run app.py

# 3 — Open in browser
# Streamlit will auto-open http://localhost:8501
```

---

## What it does

| Feature | Details |
|---|---|
| **Parse** | Dynamically discovers all 42 collection blocks and their Excel row indices |
| **Display** | Shows Jan'26–Dec'26 editable columns + Jan'25–Dec'25 read-only reference |
| **Edit** | Click any 2026 cell to edit; Tab moves to the next month |
| **Validate** | Rejects negative values and non-integer QTY on Save |
| **Save** | Writes only changed cells; preserves all Excel formulas/styles |
| **Backup** | Creates `OTB_v2_backup_YYYYMMDD_HHMMSS.xlsx` before every save |
| **Dry-Run** | Toggle in sidebar to preview changes without writing |
| **Analytics** | KPI cards + monthly bar chart + category donut chart |
| **Detail** | Per-collection 4-year sparkline + full monthly grid |

---

## File structure

```
otb_app/
├── app.py          # Main Streamlit UI (~300 lines)
├── otb_engine.py   # Excel parse/write logic (no UI dependency)
├── components.py   # Plotly charts + KPI cards + CSS
├── requirements.txt
└── README.md
```

The source Excel file lives at:
```
C:\Users\Lenovo\OneDrive\Documents\Sounada\OTB_v2.xlsx
```
You can change the path in the **sidebar → Data Source** field at any time.

---

## Editable metrics

| Col F value in Excel | Shown in UI as |
|---|---|
| `Planned Purchases USD` | Planned Purchase USD |
| `Comitted Purchase USD` *(sic)* | Committed Purchase USD |
| `Act. Goods Received USD` | COGS USD (Actual) |
| `Act. Goods Received QTY` | QTY (Actual Received) |

All other rows (formulas, derived metrics) are **never touched**.

---

## Validation rules

- All values ≥ 0 (no negatives)
- QTY columns must be whole numbers

---

## Notes

- If the file is open in Excel, save will fail gracefully with a clear message — no data is lost (backup was already created).
- Re-parsing happens automatically on Reload; the column map is discovered dynamically so future structural changes to the file are handled.
