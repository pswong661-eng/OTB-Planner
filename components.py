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
    "Planned Purchases USD":        "#1565C0",   # deep blue
    "Comitted Purchase USD":        "#2E7D32",   # deep green
    "Act. Sale USD":                "#7B1FA2",   # purple
    "Act. Sale QTY":                "#00838F",   # teal
    "Act. Goods Received QTY":      "#37474F",   # dark gray
    "Act. Stock Holding Month-USD": "#78909C",   # blue-gray (display only)
    "Act. Stock Holding Month-QTY": "#90A4AE",   # light blue-gray (display only)
}

CATEGORY_COLORS = {
    "Bdln":   "#1976D2",
    "BedAcc": "#43A047",
    "Other":  "#FB8C00",
}

PLOTLY_FONT = dict(family="Inter, system-ui, -apple-system, sans-serif", size=12)


# ─── CSS ───────────────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* ── Sidebar ─────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #1a2744 !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] small {
    color: #d4daf0 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #253563 !important;
    color: white !important;
    border-color: #3d5a99 !important;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: #253563 !important;
    color: white !important;
    border-color: #3d5a99 !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: #2d4080;
    color: white;
    border: 1px solid #3d5a99;
}

/* ── KPI cards ───────────────────────────────────────────────────── */
.kpi-card {
    background: white;
    border: 1px solid #e8eaf0;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 12px rgba(26,39,68,0.07);
    text-align: center;
    transition: box-shadow 0.2s;
}
.kpi-card:hover { box-shadow: 0 4px 20px rgba(26,39,68,0.13); }
.kpi-label {
    font-size: 10.5px;
    color: #888;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #1a2744;
    line-height: 1.1;
}
.kpi-subtext {
    font-size: 11px;
    color: #aaa;
    margin-top: 4px;
}
.kpi-accent { color: #1976D2; }

/* ── Metric badges ───────────────────────────────────────────────── */
.badge {
    display: inline-block;
    border-radius: 5px;
    padding: 2px 9px;
    font-size: 11px;
    font-weight: 600;
    margin: 3px 0;
}
.badge-blue   { background:#E3F2FD; color:#1565C0; }
.badge-green  { background:#E8F5E9; color:#2E7D32; }
.badge-orange { background:#FFF3E0; color:#E65100; }
.badge-purple { background:#F3E5F5; color:#7B1FA2; }
.badge-teal   { background:#E0F7FA; color:#00838F; }
.badge-gray   { background:#ECEFF1; color:#37474F; }

/* ── Toast notifications ─────────────────────────────────────────── */
.toast-success {
    background:#E8F5E9; border-left:4px solid #4CAF50;
    border-radius:6px; padding:12px 18px; margin:8px 0;
    font-size: 14px;
}
.toast-error {
    background:#FFEBEE; border-left:4px solid #F44336;
    border-radius:6px; padding:12px 18px; margin:8px 0;
    font-size: 14px;
}
.toast-info {
    background:#E3F2FD; border-left:4px solid #2196F3;
    border-radius:6px; padding:12px 18px; margin:8px 0;
    font-size: 14px;
}
.toast-warning {
    background:#FFF8E1; border-left:4px solid #FFC107;
    border-radius:6px; padding:12px 18px; margin:8px 0;
    font-size: 14px;
}

/* ── Page layout ─────────────────────────────────────────────────── */
.block-container { padding-top: 0.75rem !important; }
.otb-header {
    background: linear-gradient(90deg, #1a2744 0%, #2d4080 100%);
    color: white;
    padding: 14px 24px;
    border-radius: 10px;
    margin-bottom: 12px;
}
.otb-header h2 { margin: 0; font-size: 22px; font-weight: 700; }
.otb-header small { color: #a8b8d8; font-size: 12px; }

/* ── Section headers ─────────────────────────────────────────────── */
.section-title {
    font-size: 15px;
    font-weight: 600;
    color: #1a2744;
    margin: 14px 0 8px 0;
    padding-bottom: 5px;
    border-bottom: 2px solid #e8eaf0;
}

/* ── Dirty indicator ─────────────────────────────────────────────── */
.dirty-badge {
    display: inline-block;
    background: #FFF3E0;
    color: #E65100;
    border: 1px solid #FFB74D;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 8px;
}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─── KPI Cards ─────────────────────────────────────────────────────────────────
def render_kpi_cards(kpis: dict):
    """Render 4 KPI metric cards in a row."""
    c1, c2, c3, c4 = st.columns(4)

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
          "Total Planned Purchase 2026",
          f"${kpis['total_planned']:,.0f}",
          "Across all 42 collections")

    _card(c2,
          "Total Act. Sale USD 2026",
          f"${kpis['total_sale_usd']:,.0f}",
          f"QTY sold: {kpis['total_sale_qty']:,.0f} units")

    _card(c3,
          "Goods Received QTY 2026",
          f"{kpis['total_qty_received']:,.0f} units",
          "Across all collections")

    util = (kpis["total_sale_usd"] / kpis["total_planned"] * 100) if kpis["total_planned"] > 0 else 0.0
    util_color = "#2E7D32" if util >= 60 else ("#FB8C00" if util >= 30 else "#C62828")
    c4.markdown(
        f"""<div class="kpi-card">
                <div class="kpi-label">Purchase Utilisation</div>
                <div class="kpi-value" style="color:{util_color}">{util:.1f}%</div>
                <div class="kpi-subtext">Act. Sale ÷ Planned Purchase</div>
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
        title=dict(text=f"📅  Planned Purchase by Month ({year})", font=dict(size=14)),
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
        textinfo="label+percent",
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
        title=dict(text="📦  Planned Purchase by Category", font=dict(size=14)),
        height=290,
        margin=dict(l=10, r=10, t=40, b=10),
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
    st.markdown(f'<div class="toast-success">✅ {msg}</div>', unsafe_allow_html=True)


def toast_error(msg: str):
    st.markdown(f'<div class="toast-error">❌ {msg}</div>', unsafe_allow_html=True)


def toast_info(msg: str):
    st.markdown(f'<div class="toast-info">ℹ️ {msg}</div>', unsafe_allow_html=True)


def toast_warning(msg: str):
    st.markdown(f'<div class="toast-warning">⚠️ {msg}</div>', unsafe_allow_html=True)
