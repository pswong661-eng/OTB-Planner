"""Quick smoke test — run with: py smoke_test.py"""
import sys
sys.path.insert(0, '.')
from otb_engine import load_otb_data, build_dataframe, compute_kpis, MONTHS, METRIC_DISPLAY

filepath = r'C:\Users\Lenovo\OneDrive\Documents\Sounada\OTB_v2.xlsx'

print('=== Parsing OTB_v2.xlsx ===')
data = load_otb_data(filepath)
meta = data['_meta']
col_map = meta['col_map']

print(f"Sheet: OTB")
print(f"Collections discovered: {len(meta['collections'])}")
print(f"2025 col indices: {col_map['2025']}  ({len(col_map['2025'])} months)")
print(f"2026 col indices: {col_map['2026']}  ({len(col_map['2026'])} months)")
print(f"Total 2025 col: {col_map['total_2025']}")
print(f"Total 2026 col: {col_map['total_2026']}")
print()

# Spot-check AKE Earnest
key = ('AKE Earnest', 'Bdln', 'Tencel Modal')
print(f"=== Spot-check: {key} ===")
entry = data[key]
for metric in METRIC_DISPLAY.keys():
    if metric in entry:
        e = entry[metric]
        vals25 = [e['2025'][m] for m in MONTHS]
        vals26 = [e['2026'][m] for m in MONTHS]
        print(f"  [{metric}] row_idx={e['row_idx']}")
        print(f"    2025: {vals25}  | total={e['total_2025']}")
        print(f"    2026: {vals26}  | total={e['total_2026']}")
print()

# Build DataFrame
df = build_dataframe(data, edit_year='2026', ref_year='2025')
print(f"=== DataFrame: {df.shape[0]} rows x {df.shape[1]} cols ===")
print(f"Unique collections: {df['Collection'].nunique()}")
print(f"Rows per metric:")
for m, c in df['_metric'].value_counts().items():
    print(f"  {m}: {c}")
print()

# KPIs
kpis = compute_kpis(data, edit_year='2026')
print("=== KPIs (2026) ===")
print(f"  Total Planned:   ${kpis['total_planned']:,.0f}")
print(f"  Total Committed: ${kpis['total_committed']:,.0f}")
print(f"  Commitment Rate: {kpis['commitment_rate']:.1f}%")
print(f"  Total Sale USD:  ${kpis['total_sale_usd']:,.0f}")
print(f"  Total Sale QTY:  {kpis['total_sale_qty']:,.0f}")
print(f"  Total Rcv QTY:   {kpis['total_qty_received']:,.0f}")
print(f"  By Category:     {kpis['by_category']}")

print()
print("=== ALL COLLECTIONS ===")
n_expected = len(METRIC_DISPLAY)
ok = 0
missing_metrics = []
for k in meta['collections']:
    col, cat, seg = k
    found = [m for m in METRIC_DISPLAY.keys() if m in data[k]]
    missing = [m for m in METRIC_DISPLAY.keys() if m not in data[k]]
    if not missing:
        ok += 1
    else:
        missing_metrics.append((k, missing))
    print(f"  {col} | {cat} | {seg}  --> {len(found)}/{n_expected} metrics")

print()
print(f"Collections with all {n_expected} metrics: {ok}/{len(meta['collections'])}")
if missing_metrics:
    print("Collections missing metrics:")
    for k, missing in missing_metrics:
        print(f"  {k}: missing {missing}")

print()
print("PARSE OK - app is ready to launch.")
print("  Run: streamlit run app.py")
