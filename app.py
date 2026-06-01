"""
app.py — OTB Planner  (Streamlit)

Run with:
    streamlit run app.py
"""

import glob
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ── make sure local modules are importable ─────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from otb_engine import (
    EDITABLE_METRICS,
    DISPLAY_METRICS,
    METRIC_DISPLAY,
    MONTHS,
    build_dataframe,
    compute_kpis,
    detect_changes,
    load_otb_data,
    save_changes,
    validate_changes,
)
from components import (
    inject_css,
    metric_badge,
    planned_by_category_chart,
    planned_monthly_chart,
    render_kpi_cards,
    sparkline_chart,
    toast_error,
    toast_info,
    toast_success,
    toast_warning,
    METRIC_COLORS,
)

# ─── Configuration ─────────────────────────────────────────────────────────────
EDIT_YEAR = "2026"
REF_YEAR  = "2025"

# Try common locations; user can override in sidebar
_CANDIDATE_PATHS = [
    Path(__file__).parent / "OTB_v2.xlsx",
    Path(r"C:\Users\Lenovo\OneDrive\Documents\Sounada\OTB_v2.xlsx"),
    Path(r"C:\Users\Lenovo\OneDrive\Documents\Sounada\OTB_v2_Feb2026.xlsx"),
]
DEFAULT_PATH = next((str(p) for p in _CANDIDATE_PATHS if p.exists()),
                    str(_CANDIDATE_PATHS[1]))

EY2 = EDIT_YEAR[2:]   # "26"
RY2 = REF_YEAR[2:]    # "25"

MONTH_COLS_26 = [f"{m}'{EY2}" for m in MONTHS]
MONTH_COLS_25 = [f"{m}'{RY2} ◀" for m in MONTHS]
TOTAL_COL_26  = f"Total {EDIT_YEAR}"
TOTAL_COL_25  = f"Total {REF_YEAR} ◀"

DISPLAY_COLS = (
    ["Collection", "Category", "Segment", "Metric"]
    + MONTH_COLS_26
    + [TOTAL_COL_26]
)
REF_COLS = MONTH_COLS_25 + [TOTAL_COL_25]
INTERNAL_COLS = ["_row_idx", "_key", "_metric"]


# ─── File discovery ────────────────────────────────────────────────────────────
_SCAN_DIRS = [
    r"C:\Users\Lenovo\OneDrive\Documents\Sounada",
    r"C:\Users\Lenovo\OneDrive\Documents\LaoPride",
    r"C:\Users\Lenovo\OneDrive\Documents",
    r"C:\Users\Lenovo\Downloads",
    str(Path(__file__).parent),
]

def _discover_xlsx() -> list[str]:
    found = []
    for d in _SCAN_DIRS:
        for fp in glob.glob(os.path.join(d, "*.xlsx")):
            if fp not in found:
                found.append(fp)
    return sorted(found)


# ─── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OTB Planner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


# ─── Session state bootstrap ───────────────────────────────────────────────────
def _init():
    defaults = {
        "filepath":          DEFAULT_PATH,
        "data":              None,
        "df_original":       None,
        "df_edited":         None,
        "last_saved":        None,
        "dry_run":           False,
        "_cache_bust":       0,
        "filter_category":   "All",
        "filter_segment":    "All",
        "filter_collection": "",
        "show_ref":          False,
        "notify":            [],    # list of (kind, message) to display once
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="⏳  Loading OTB data from Excel…")
def _cached_load(filepath: str, bust: int) -> dict:
    return load_otb_data(filepath)


def load_data(filepath: str | None = None) -> bool:
    """Load (or re-load) data into session state.  Returns True on success."""
    fp = filepath or st.session_state.filepath
    if not os.path.exists(fp):
        st.error(f"File not found:\n\n`{fp}`\n\nUpdate the path in the sidebar.")
        return False
    try:
        data = _cached_load(fp, st.session_state._cache_bust)
        df   = build_dataframe(data, edit_year=EDIT_YEAR, ref_year=REF_YEAR)
        st.session_state.data        = data
        st.session_state.df_original = df.copy()
        st.session_state.df_edited   = df.copy()
        return True
    except Exception as exc:
        st.error(f"Failed to parse Excel: {exc}")
        return False


# ─── Filtering helpers ─────────────────────────────────────────────────────────
def _filtered_df() -> pd.DataFrame:
    df = st.session_state.df_edited
    if df is None or df.empty:
        return pd.DataFrame()

    mask = pd.Series([True] * len(df), index=df.index)

    cat = st.session_state.filter_category
    if cat != "All":
        mask &= df["Category"] == cat

    seg = st.session_state.filter_segment
    if seg != "All":
        mask &= df["Segment"] == seg

    search = st.session_state.filter_collection.strip().lower()
    if search:
        mask &= df["Collection"].str.lower().str.contains(search, na=False)

    return df[mask].copy()


# ─── Pending-change detection ──────────────────────────────────────────────────
def _pending_changes() -> list:
    if st.session_state.df_edited is None:
        return []
    return detect_changes(
        st.session_state.data,
        st.session_state.df_edited,
        edit_year=EDIT_YEAR,
    )


# ─── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 📊 OTB Planner")
        st.caption(f"Edit Year: **{EDIT_YEAR}** | Ref: **{REF_YEAR}**")
        st.markdown("---")

        # --- File picker ---
        st.markdown("### 📁 Data Source")

        xlsx_files = _discover_xlsx()
        cur = st.session_state.filepath

        # Build selectbox options: discovered files + "Enter path manually"
        MANUAL = "✏️  Enter path manually…"
        options = xlsx_files + [MANUAL]
        default_idx = options.index(cur) if cur in options else len(options) - 1

        chosen = st.selectbox(
            "Select Excel file",
            options,
            index=default_idx,
            key="_fp_select",
            format_func=lambda p: os.path.basename(p) if p != MANUAL else MANUAL,
            help="Scans common folders for .xlsx files",
        )

        if chosen == MANUAL:
            new_fp = st.text_input(
                "File path",
                value=cur,
                key="_fp_input",
                placeholder=r"C:\...\OTB_v2.xlsx",
            )
        else:
            new_fp = chosen
            st.caption(f"`{new_fp}`")

        if new_fp and new_fp != cur:
            st.session_state.filepath    = new_fp
            st.session_state._cache_bust += 1
            st.rerun()

        if st.button("🔄 Reload", use_container_width=True):
            st.session_state._cache_bust += 1
            load_data()
            st.rerun()

        # --- Dry-run toggle ---
        st.markdown("---")
        st.markdown("### ⚙️ Options")
        st.toggle(
            "Dry-Run Mode",
            value=st.session_state.dry_run,
            key="dry_run",
            help="Preview what would be written without touching the file.",
        )
        show_ref = st.toggle(
            "Show 2025 Reference Columns",
            value=st.session_state.show_ref,
            key="show_ref",
            help="Append read-only 2025 actuals to the right of the table.",
        )

        # --- Filters ---
        df = st.session_state.df_edited
        if df is not None and not df.empty:
            st.markdown("---")
            st.markdown("### 🔍 Filters")

            cats = ["All"] + sorted(df["Category"].dropna().unique())
            cat_val = st.session_state.filter_category
            if cat_val not in cats:
                cat_val = "All"
            st.selectbox("Category", cats,
                         index=cats.index(cat_val),
                         key="filter_category")

            if st.session_state.filter_category != "All":
                segs_raw = (
                    df[df["Category"] == st.session_state.filter_category]["Segment"]
                    .dropna().unique()
                )
            else:
                segs_raw = df["Segment"].dropna().unique()
            segs = ["All"] + sorted(segs_raw)
            seg_val = st.session_state.filter_segment
            if seg_val not in segs:
                seg_val = "All"
            st.selectbox("Segment", segs,
                         index=segs.index(seg_val),
                         key="filter_segment")

            st.text_input(
                "Search collection",
                value=st.session_state.filter_collection,
                key="filter_collection",
                placeholder="e.g. AKE Earnest…",
            )

            filtered = _filtered_df()
            n = filtered["Collection"].nunique() if not filtered.empty else 0
            total_n = df["Collection"].nunique()
            st.caption(f"Showing **{n}** of **{total_n}** collections")

        # --- Status ---
        st.markdown("---")
        changes = _pending_changes()
        if changes:
            st.markdown(
                f'<span class="dirty-badge">✏️ {len(changes)} unsaved change(s)</span>',
                unsafe_allow_html=True,
            )
        if st.session_state.last_saved:
            st.caption(f"Last saved: {st.session_state.last_saved}")


# ─── Save handler ──────────────────────────────────────────────────────────────
def handle_save():
    changes = _pending_changes()

    if not changes:
        toast_info("No changes to save.")
        return

    errors = validate_changes(changes)
    if errors:
        for e in errors:
            toast_error(f"Validation: {e}")
        return

    if st.session_state.dry_run:
        result = save_changes(st.session_state.filepath, changes, dry_run=True)
        toast_warning(f"**Dry-Run** — {result['written']} cell(s) would be written:")
        for line in result.get("preview", []):
            st.code(line, language=None)
        return

    result = save_changes(st.session_state.filepath, changes, dry_run=False)

    if result["success"]:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.last_saved = ts
        toast_success(
            f"Saved **{result['written']}** cell(s) to `OTB_v2.xlsx`  —  {ts}  \n"
            f"<small>Backup: `{result['backup_path']}`</small>"
        )
        # Reload to reset dirty state
        st.session_state._cache_bust += 1
        load_data()
        st.rerun()
    else:
        for e in result["errors"]:
            toast_error(e)


# ─── Main data table ───────────────────────────────────────────────────────────
def render_main_table():
    filtered = _filtered_df()

    if filtered.empty:
        st.info("No collections match the current filters.")
        return

    # Recompute totals live (don't trust Excel formula values in the DF)
    filtered[TOTAL_COL_26] = filtered[MONTH_COLS_26].sum(axis=1)
    filtered[TOTAL_COL_25] = filtered[MONTH_COLS_25].sum(axis=1)

    # Split editable vs display-only rows
    editable_df = filtered[filtered["_editable"] == True].copy()
    display_df  = filtered[filtered["_editable"] == False].copy()

    # ── EDITABLE TABLE ──────────────────────────────────────────────────────────
    show_cols = DISPLAY_COLS.copy()
    if st.session_state.show_ref:
        show_cols += REF_COLS

    internal_cols_ext = INTERNAL_COLS + ["_editable"]
    show_df = editable_df[show_cols + internal_cols_ext].reset_index(drop=True)

    col_cfg: dict = {
        "Collection": st.column_config.TextColumn("Collection", disabled=True, width="medium"),
        "Category":   st.column_config.TextColumn("Cat.",       disabled=True, width="small"),
        "Segment":    st.column_config.TextColumn("Segment",    disabled=True, width="medium"),
        "Metric":     st.column_config.TextColumn("Metric",     disabled=True, width="medium"),
    }
    for col in MONTH_COLS_26:
        col_cfg[col] = st.column_config.NumberColumn(
            col, min_value=0, format="%.0f", width="small",
            help="Enter value (USD or QTY). 0 = empty."
        )
    col_cfg[TOTAL_COL_26] = st.column_config.NumberColumn(
        TOTAL_COL_26, disabled=True, format="%.0f", width="small"
    )
    for col in MONTH_COLS_25 + [TOTAL_COL_25]:
        col_cfg[col] = st.column_config.NumberColumn(
            col, disabled=True, format="%.0f", width="small"
        )
    for col in internal_cols_ext:
        col_cfg[col] = st.column_config.Column(col, disabled=True, width=0)

    table_height = min(900, max(300, len(show_df) * 36 + 52))

    editor_key = f"main_table_editor_{st.session_state._cache_bust}"

    edited: pd.DataFrame = st.data_editor(
        show_df,
        column_config=col_cfg,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        height=table_height,
        key=editor_key,
    )

    # ── DISPLAY-ONLY TABLE (Stock Holding) ──────────────────────────────────────
    if not display_df.empty:
        with st.expander(
            f"📊 Stock Holding Reference ({len(display_df['Collection'].unique())} collections — read-only)",
            expanded=False,
        ):
            disp_show = display_df[show_cols + internal_cols_ext].reset_index(drop=True)
            disp_cfg = dict(col_cfg)
            # All 2026 month cols are disabled for display metrics
            for col in MONTH_COLS_26 + [TOTAL_COL_26]:
                disp_cfg[col] = st.column_config.NumberColumn(
                    col, disabled=True, format="%.0f", width="small"
                )
            st.dataframe(
                disp_show[show_cols],
                column_config=disp_cfg,
                use_container_width=True,
                hide_index=True,
            )

    # ── Merge edits back into df_edited (only changed cells) ────────────────────
    if edited is not None and not edited.empty:
        for i, edited_row in edited.iterrows():
            rid = edited_row["_row_idx"]
            mask = st.session_state.df_edited["_row_idx"] == rid
            if not mask.any():
                continue
            orig_row = show_df[show_df["_row_idx"] == rid]
            if orig_row.empty:
                continue
            for col in MONTH_COLS_26:
                if col not in edited_row.index:
                    continue
                new_val = edited_row[col]
                orig_val = orig_row.iloc[0][col]
                # Only write back cells the user actually changed
                if abs(float(new_val or 0) - float(orig_val or 0)) > 0.0001:
                    st.session_state.df_edited.loc[mask, col] = new_val

    # ── Legend ───────────────────────────────────────────────────────────────────
    st.markdown(
        "  ".join(metric_badge(m) for m in EDITABLE_METRICS),
        unsafe_allow_html=True,
    )


# ─── Collection detail drawer ──────────────────────────────────────────────────
def render_detail_tab():
    data = st.session_state.data
    if data is None:
        return

    meta = data["_meta"]
    collections = meta["collections"]

    options_map = {
        f"{k[0]}  ({k[1]} / {k[2]})": k
        for k in collections
    }
    label_list = ["— select a collection —"] + sorted(options_map)

    chosen_label = st.selectbox("Collection", label_list, key="detail_select")
    if chosen_label == "— select a collection —":
        return

    key = options_map[chosen_label]
    collection, category, segment = key

    # ── Sparkline trend ─────────────────────────────────────────────────────────
    fig_spark = sparkline_chart(data, key, year=EDIT_YEAR)
    st.plotly_chart(fig_spark, use_container_width=True)

    # ── 12-month grid per metric ─────────────────────────────────────────────────
    col_labels_26 = [f"{m}'{EY2}" for m in MONTHS]
    col_labels_25 = [f"{m}'{RY2} (ref)" for m in MONTHS]

    st.markdown(
        f'<div class="section-title">📋  {collection} — Monthly Breakdown</div>',
        unsafe_allow_html=True,
    )

    def _render_metric_block(metric: str, is_display_only: bool = False):
        """Render one metric's 14-column (header + 12 months + total) grid."""
        if metric not in data[key]:
            return

        entry   = data[key][metric]
        disp    = METRIC_DISPLAY.get(metric, metric)
        color   = METRIC_COLORS.get(metric, "#546E7A")
        is_qty  = "QTY" in metric or "Month" in metric
        fmt_val = (lambda v: f"{v:,.0f}") if is_qty else (lambda v: f"${v:,.0f}")

        # Label tag — muted style for display-only metrics
        if is_display_only:
            tag_style = (
                f"background:#ECEFF1;color:#546E7A;display:inline-block;"
                f"padding:3px 10px;border-radius:5px;font-size:11px;font-weight:600;"
                f"margin:10px 0 4px 0;border:1px dashed #B0BEC5;"
            )
            tag_suffix = " ◀ read-only"
        else:
            tag_style = (
                f"background:{color};color:white;display:inline-block;"
                f"padding:4px 12px;border-radius:5px;font-size:12px;font-weight:600;"
                f"margin:10px 0 6px 0;"
            )
            tag_suffix = ""

        st.markdown(
            f'<div style="{tag_style}">{disp}{tag_suffix}</div>',
            unsafe_allow_html=True,
        )

        vals_26 = entry.get(EDIT_YEAR, {})
        vals_25 = entry.get(REF_YEAR,  {})
        tot_26  = sum((vals_26.get(m) or 0) for m in MONTHS)
        tot_25  = sum((vals_25.get(m) or 0) for m in MONTHS)

        # Header row
        hcols = st.columns(14)
        hcols[0].markdown("**Year**")
        for i, lbl in enumerate(col_labels_26):
            hcols[i + 1].markdown(f"<small style='color:#777'>{lbl}</small>",
                                  unsafe_allow_html=True)
        hcols[13].markdown("<small style='color:#777'>**Total**</small>",
                           unsafe_allow_html=True)

        # 2026 row
        row_26 = st.columns(14)
        val_weight = "normal" if is_display_only else "bold"
        row_26[0].markdown(f"**{EDIT_YEAR}**")
        for i, month in enumerate(MONTHS):
            v = vals_26.get(month, 0) or 0
            row_26[i + 1].markdown(
                f"<span style='font-weight:{val_weight}'>{fmt_val(v)}</span>",
                unsafe_allow_html=True,
            )
        row_26[13].markdown(
            f"<span style='font-weight:{val_weight}'>{fmt_val(tot_26)}</span>",
            unsafe_allow_html=True,
        )

        # 2025 reference row
        row_25 = st.columns(14)
        row_25[0].markdown(
            f"<span style='color:#999'>{REF_YEAR} ◀</span>",
            unsafe_allow_html=True,
        )
        for i, month in enumerate(MONTHS):
            v = vals_25.get(month, 0) or 0
            row_25[i + 1].markdown(
                f"<span style='color:#aaa;font-size:11px'>{fmt_val(v)}</span>",
                unsafe_allow_html=True,
            )
        row_25[13].markdown(
            f"<span style='color:#aaa;font-size:11px'>{fmt_val(tot_25)}</span>",
            unsafe_allow_html=True,
        )

    # Editable metrics
    for metric in EDITABLE_METRICS:
        _render_metric_block(metric, is_display_only=False)

    # Display-only metrics (Stock Holding)
    st.markdown(
        '<div class="section-title" style="margin-top:18px;">📊 Stock Holding (read-only)</div>',
        unsafe_allow_html=True,
    )
    for metric in DISPLAY_METRICS:
        _render_metric_block(metric, is_display_only=True)

    st.markdown("---")
    remarks_row = data[key].get("_remarks_row")
    if remarks_row:
        st.caption(f"Excel remarks row: {remarks_row}")


# ─── Analytics section ─────────────────────────────────────────────────────────
def render_analytics():
    data = st.session_state.data
    if data is None:
        return
    kpis = compute_kpis(data, edit_year=EDIT_YEAR)

    with st.expander("📈 Analytics Dashboard", expanded=True):
        render_kpi_cards(kpis)

        st.markdown("<br>", unsafe_allow_html=True)
        c_bar, c_pie = st.columns([3, 2])

        with c_bar:
            fig_bar = planned_monthly_chart(kpis, year=EDIT_YEAR)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c_pie:
            fig_pie = planned_by_category_chart(kpis)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No planned purchase data yet.")


# ─── Top header ────────────────────────────────────────────────────────────────
def render_header():
    last_saved = st.session_state.last_saved or "Not saved yet"
    changes    = _pending_changes()

    # Build sub-strings separately to avoid f-string nesting issues
    dirty_html   = f'&nbsp;<span class="dirty-badge">&#9998; {len(changes)} pending</span>' if changes else ""
    dry_run_html = "&nbsp;&middot;&nbsp;<b>DRY-RUN ON</b>" if st.session_state.dry_run else ""

    header_html = (
        '<div class="otb-header">'
        f'<h2>&#128202; OTB Planner &nbsp;'
        f'<span style="font-size:14px;font-weight:400;">2026 Open-to-Buy</span>'
        f'{dirty_html}</h2>'
        f'<p style="margin:0;color:#a8b8d8;font-size:12px;">'
        f'Last saved: {last_saved}{dry_run_html}</p>'
        '</div>'
    )

    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown(header_html, unsafe_allow_html=True)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save to Excel", type="primary",
                     use_container_width=True, key="save_btn"):
            handle_save()


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    _init()

    # Bootstrap data
    if st.session_state.data is None:
        if not load_data():
            st.markdown(
                "### Setup\n"
                "Update the **Excel file path** in the sidebar, then click **Reload**."
            )
            render_sidebar()
            st.stop()

    render_sidebar()
    render_header()
    render_analytics()
    st.markdown("---")

    tab_data, tab_detail = st.tabs(["📋 Data Entry  ", "🔍 Collection Detail  "])

    with tab_data:
        st.markdown(
            '<div class="section-title">2026 Monthly Data (editable) — '
            'click any Jan\'26–Dec\'26 cell to edit, Tab to advance</div>',
            unsafe_allow_html=True,
        )
        render_main_table()

    with tab_detail:
        render_detail_tab()


if __name__ == "__main__":
    main()
