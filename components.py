"""
components.py — Reusable UI components for the OTB Planner.
All functions return either Streamlit widgets or Plotly figures.
"""
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from otb_engine import MONTHS, METRIC_DISPLAY, EDITABLE_METRICS

# ─── Color palette ─────────────────────────────────────────────────────────────
METRIC_COLORS = {
    "Planned Purchases USD":        "#2563EB",
    "Comitted Purchase USD":        "#0F766E",
    "Act. Sale USD":                "#7C3AED",
    "Act. Sale QTY":                "#0891B2",
    "Act. Goods Received QTY":      "#475569",
    "Act. Stock Holding Month-USD": "#64748B",
    "Act. Stock Holding Month-QTY": "#94A3B8",
}

CATEGORY_COLORS = {
    "Bdln":   "#2563EB",
    "BedAcc": "#0F766E",
    "Other":  "#D97706",
}

PLOTLY_FONT = dict(family="Inter, system-ui, -apple-system, sans-serif", size=12)


# ─── CSS ───────────────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    color: #0F172A;
}
.stApp {
    background: #F8FAFC;
}
.block-container {
    max-width: 1440px;
    padding-top: 1rem !important;
    padding-bottom: 2rem;
}

section[data-testid="stSidebar"] {
    background: #0F172A !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] small {
    color: #CBD5E1 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1E293B !important;
    color: white !important;
    border-color: #334155 !important;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: #1E293B !important;
    color: white !important;
    border-color: #334155 !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: #1E293B;
    color: white;
    border: 1px solid #334155;
}
div.stButton > button[kind="primary"],
div.stDownloadButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] {
    background: #2563EB !important;
    border-color: #2563EB !important;
    color: white !important;
}
div.stButton > button[kind="primary"]:hover,
div.stDownloadButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
    background: #1D4ED8 !important;
    border-color: #1D4ED8 !important;
    color: white !important;
}

.kpi-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    text-align: left;
}
.kpi-label {
    font-size: 11px;
    color: #64748B;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 24px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.1;
}
.kpi-subtext {
    font-size: 12px;
    color: #64748B;
    margin-top: 4px;
}
.kpi-accent { color: #2563EB; }

.badge {
    display: inline-block;
    border-radius: 6px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: 600;
    margin: 3px 0;
}
.badge-blue   { background:#EFF6FF; color:#1D4ED8; }
.badge-green  { background:#F0FDFA; color:#0F766E; }
.badge-orange { background:#FFF7ED; color:#C2410C; }
.badge-purple { background:#F5F3FF; color:#6D28D9; }
.badge-teal   { background:#ECFEFF; color:#0E7490; }
.badge-gray   { background:#F1F5F9; color:#475569; }

.toast-success {
    background:#F0FDF4; border-left:4px solid #16A34A;
    border-radius:8px; padding:12px 18px; margin:8px 0;
    font-size: 14px;
}
.toast-error {
    background:#FEF2F2; border-left:4px solid #DC2626;
    border-radius:8px; padding:12px 18px; margin:8px 0;
    font-size: 14px;
}
.toast-info {
    background:#EFF6FF; border-left:4px solid #2563EB;
    border-radius:8px; padding:12px 18px; margin:8px 0;
    font-size: 14px;
}
.toast-warning {
    background:#FFFBEB; border-left:4px solid #D97706;
    border-radius:8px; padding:12px 18px; margin:8px 0;
    font-size: 14px;
}

.otb-header {
    background: white;
    color: #0F172A;
    padding: 18px 20px;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
    margin-bottom: 14px;
    box-shadow: 0 1px 2px rgba(15,23,42,0.04);
}
.otb-header h2 { margin: 0; font-size: 24px; font-weight: 700; letter-spacing: 0; }
.otb-header small { color: #64748B; font-size: 12px; }

.section-title {
    font-size: 16px;
    font-weight: 600;
    color: #0F172A;
    margin: 16px 0 8px 0;
}

.dirty-badge {
    display: inline-block;
    background: #FFF7ED;
    color: #C2410C;
    border: 1px solid #FED7AA;
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 8px;
}
.source-pill {
    display: inline-block;
    background: #F8FAFC;
    color: #334155;
    border: 1px solid #E2E8F0;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 600;
}
.workbench-panel {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 2px rgba(15,23,42,0.04);
}
.exception-item {
    background: white;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #D97706;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.exception-high { border-left-color: #DC2626; }
.exception-medium { border-left-color: #D97706; }
.exception-low { border-left-color: #2563EB; }
.exception-title {
    color: #0F172A;
    font-size: 14px;
    font-weight: 700;
}
.exception-meta {
    color: #64748B;
    font-size: 12px;
    margin-top: 2px;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    height: 38px;
    padding: 0 14px;
    border-radius: 8px 8px 0 0;
    color: #334155;
    font-size: 13px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    color: #2563EB !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #2563EB !important;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    overflow: hidden;
}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─── KPI Cards ─────────────────────────────────────────────────────────────────
def render_kpi_cards(kpis: dict):
    """Render KPI metric cards in a row."""
    c1, c2, c3, c4, c5 = st.columns(5)

    def _card(col, label, value_str, subtext, accent=False):
        cls = "kpi-accent" if accent else ""
        col.markdown(
            f"""<div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value {cls}">{value_str}</div>
                    <div class="kpi-subtext">{subtext}</div>
                </div>""",
            unsafe_allow_html=True,
        )

    _card(c1,
          "Planned Buy",
          f"${kpis['total_planned']:,.0f}",
          "2026 open-to-buy plan")

    _card(c2,
          "Actual Sales",
          f"${kpis['total_sale_usd']:,.0f}",
          f"{kpis['total_sale_qty']:,.0f} units sold")

    _card(c3,
          "Received QTY",
          f"{kpis['total_qty_received']:,.0f} units",
          "Goods received")

    util = (kpis["total_sale_usd"] / kpis["total_planned"] * 100) if kpis["total_planned"] > 0 else 0.0
    util_color = "#0F766E" if util >= 60 else ("#D97706" if util >= 30 else "#DC2626")
    c4.markdown(
        f"""<div class="kpi-card">
                <div class="kpi-label">Sell-through proxy</div>
                <div class="kpi-value" style="color:{util_color}">{util:.1f}%</div>
                <div class="kpi-subtext">Sales divided by planned buy</div>
            </div>""",
        unsafe_allow_html=True,
    )
    remaining = kpis["total_planned"] - kpis["total_sale_usd"]
    rem_color = "#0F766E" if remaining >= 0 else "#DC2626"
    c5.markdown(
        f"""<div class="kpi-card">
                <div class="kpi-label">Remaining OTB</div>
                <div class="kpi-value" style="color:{rem_color}">${remaining:,.0f}</div>
                <div class="kpi-subtext">Planned buy less actual sales</div>
            </div>""",
        unsafe_allow_html=True,
    )


# ─── Bar Chart: Planned Purchase by Month ──────────────────────────────────────
def planned_monthly_chart(kpis: dict, year: str = "2026") -> go.Figure:
    month_labels = [f"{m}'{year[2:]}" for m in MONTHS]
    planned = [kpis["monthly_planned"][m] for m in MONTHS]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=month_labels, y=planned,
        name="Planned Purchase",
        marker_color="#1976D2",
        opacity=0.88,
        hovertemplate="<b>%{x}</b><br>Planned: $%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text=f"Monthly Planned Buy ({year})", font=dict(size=14)),
        height=290,
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(tickprefix="$", tickformat=",", gridcolor="#f0f2f5",
                   showgrid=True, zeroline=False),
        xaxis=dict(showgrid=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=PLOTLY_FONT,
    )
    return fig


# ─── Donut Chart: Planned by Category ─────────────────────────────────────────
def planned_by_category_chart(kpis: dict) -> go.Figure:
    by_cat = {k: v for k, v in kpis["planned_by_category"].items() if v > 0}
    if not by_cat:
        return None

    labels = list(by_cat.keys())
    values = list(by_cat.values())
    colors = [CATEGORY_COLORS.get(l, "#90A4AE") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="none",
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f} (%{percent})<extra></extra>",
    ))

    total = sum(values)
    fig.add_annotation(
        text=f"${total:,.0f}",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="#1a2744", family="Inter"),
    )

    fig.update_layout(
        title=dict(text="Planned Buy by Category", font=dict(size=14)),
        height=290,
        margin=dict(l=0, r=0, t=40, b=10),
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=11)),
        paper_bgcolor="white",
        font=PLOTLY_FONT,
    )
    return fig


# ─── Sparkline for detail drawer ───────────────────────────────────────────────
def sparkline_chart(data: dict, key: tuple, year: str = "2026") -> go.Figure:
    """Mini 4-year trend chart for Planned Purchase."""
    entry_planned = data[key].get("Planned Purchases USD", {})

    years = ["2023", "2024", "2025", year]
    planned_totals = [
        sum((entry_planned.get(yr, {}).get(m, 0) or 0) for m in MONTHS)
        for yr in years
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=planned_totals,
        mode="lines+markers", name="Planned",
        line=dict(color="#1976D2", width=2),
        marker=dict(size=7),
    ))
    collection_name = key[0]
    fig.update_layout(
        title=dict(text=f"Annual Trend — {collection_name}", font=dict(size=13)),
        height=200,
        margin=dict(l=10, r=10, t=36, b=10),
        yaxis=dict(tickprefix="$", tickformat=",", gridcolor="#f0f2f5", showgrid=True),
        xaxis=dict(showgrid=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=PLOTLY_FONT,
    )
    return fig


# ─── Metric color badge ────────────────────────────────────────────────────────
BADGE_CLASSES = {
    "Planned Purchases USD":        "badge-blue",
    "Comitted Purchase USD":        "badge-green",
    "Act. Sale USD":                "badge-purple",
    "Act. Sale QTY":                "badge-teal",
    "Act. Goods Received QTY":      "badge-gray",
    "Act. Stock Holding Month-USD": "badge-gray",
    "Act. Stock Holding Month-QTY": "badge-gray",
}


def metric_badge(metric_key: str) -> str:
    cls = BADGE_CLASSES.get(metric_key, "badge-gray")
    display = METRIC_DISPLAY.get(metric_key, metric_key)
    return f'<span class="badge {cls}">{display}</span>'


# ─── Toast helpers ─────────────────────────────────────────────────────────────
def toast_success(msg: str):
    st.markdown(f'<div class="toast-success">{msg}</div>', unsafe_allow_html=True)


def toast_error(msg: str):
    st.markdown(f'<div class="toast-error">{msg}</div>', unsafe_allow_html=True)


def toast_info(msg: str):
    st.markdown(f'<div class="toast-info">{msg}</div>', unsafe_allow_html=True)


def toast_warning(msg: str):
    st.markdown(f'<div class="toast-warning">{msg}</div>', unsafe_allow_html=True)
