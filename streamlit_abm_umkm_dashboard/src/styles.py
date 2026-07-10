import streamlit as st


def inject_custom_css() -> None:
    """Clean, professional CSS — inspired by Vercel/Linear design language."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

        /* ── Canvas ──────────────────────────────────────── */
        .main { background: #0A0A0B; }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        /* ── Sidebar ─────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: #111113;
            border-right: 1px solid #1F1F23;
        }
        [data-testid="stSidebar"] * { color: #A1A1AA !important; }
        [data-testid="stSidebar"] .stMarkdown h1 {
            color: #FAFAFA !important;
            font-weight: 600 !important;
            font-size: 18px !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: transparent;
            border: 1px solid #1F1F23;
            border-radius: 10px;
            margin-bottom: 6px;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: #FAFAFA;
            color: #0A0A0B !important;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            padding: 10px 16px;
            transition: opacity 0.2s ease;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            opacity: 0.85;
        }

        /* ── Metric Cards ────────────────────────────────── */
        div[data-testid="stMetric"] {
            background: #111113;
            border: 1px solid #1F1F23;
            padding: 18px 18px;
            border-radius: 12px;
            transition: border-color 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            border-color: #27272A;
        }
        div[data-testid="stMetric"] label {
            color: #71717A !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #FAFAFA !important;
            font-weight: 600 !important;
            font-size: 20px !important;
        }

        /* ── Hero ────────────────────────────────────────── */
        .hero-card {
            background: #111113;
            border: 1px solid #1F1F23;
            padding: 32px 32px;
            border-radius: 16px;
            margin-bottom: 20px;
        }
        .hero-title {
            font-size: 26px;
            font-weight: 700;
            color: #FAFAFA;
            line-height: 1.2;
            margin-bottom: 8px;
        }
        .hero-subtitle {
            font-size: 14px;
            color: #71717A;
            max-width: 720px;
            line-height: 1.6;
        }
        .hero-badge {
            display: inline-block;
            background: #18181B;
            border: 1px solid #27272A;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            color: #A1A1AA;
            margin-top: 14px;
        }

        /* ── Cards ───────────────────────────────────────── */
        .glass-card {
            background: #111113;
            border: 1px solid #1F1F23;
            padding: 20px 22px;
            border-radius: 12px;
            margin-bottom: 14px;
        }

        .info-card {
            background: #111113;
            border: 1px solid #1F1F23;
            border-left: 3px solid #3B82F6;
            padding: 16px 20px;
            border-radius: 0 10px 10px 0;
            margin: 12px 0;
        }
        .info-card-success {
            background: #111113;
            border: 1px solid #1F1F23;
            border-left: 3px solid #22C55E;
            padding: 16px 20px;
            border-radius: 0 10px 10px 0;
            margin: 12px 0;
        }
        .info-card-warning {
            background: #111113;
            border: 1px solid #1F1F23;
            border-left: 3px solid #EAB308;
            padding: 16px 20px;
            border-radius: 0 10px 10px 0;
            margin: 12px 0;
        }
        .info-card-danger {
            background: #111113;
            border: 1px solid #1F1F23;
            border-left: 3px solid #EF4444;
            padding: 16px 20px;
            border-radius: 0 10px 10px 0;
            margin: 12px 0;
        }

        /* ── Section headings ────────────────────────────── */
        .section-title {
            font-size: 20px;
            font-weight: 600;
            color: #FAFAFA;
            margin: 6px 0 4px 0;
        }
        .section-desc {
            color: #71717A;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 16px;
        }

        /* ── Pills & muted text ──────────────────────────── */
        .scenario-pill {
            display: inline-block;
            padding: 5px 12px;
            margin: 3px 4px 3px 0;
            border-radius: 6px;
            background: #18181B;
            color: #D4D4D8 !important;
            border: 1px solid #27272A;
            font-size: 13px;
            font-weight: 600;
        }
        .small-muted {
            color: #52525B;
            font-size: 13px;
        }

        /* ── Footer ──────────────────────────────────────── */
        .footer-note {
            color: #3F3F46;
            font-size: 12px;
            text-align: center;
            padding: 24px 0 6px 0;
            border-top: 1px solid #1F1F23;
            margin-top: 28px;
        }

        /* ── Tabs ────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background: transparent;
            border-bottom: 1px solid #1F1F23;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 6px 6px 0 0;
            border: none;
            padding: 10px 18px;
            color: #71717A !important;
            font-weight: 500;
            font-size: 14px;
            transition: color 0.15s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #D4D4D8 !important;
        }
        .stTabs [aria-selected="true"] {
            color: #FAFAFA !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #FAFAFA !important;
            height: 2px;
        }

        /* ── Tables ──────────────────────────────────────── */
        [data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #1F1F23;
        }

        /* ── Expanders ───────────────────────────────────── */
        .streamlit-expanderHeader {
            font-weight: 500 !important;
            font-size: 14px !important;
        }

        /* ── Download button ─────────────────────────────── */
        .stDownloadButton > button {
            background: #18181B !important;
            border: 1px solid #27272A !important;
            color: #D4D4D8 !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: border-color 0.2s ease !important;
        }
        .stDownloadButton > button:hover {
            border-color: #3F3F46 !important;
        }

        /* ── Flow steps ──────────────────────────────────── */
        .flow-step {
            background: #111113;
            border: 1px solid #1F1F23;
            border-radius: 10px;
            padding: 14px 14px;
            text-align: center;
        }
        .flow-step-num {
            font-size: 22px;
            font-weight: 700;
            color: #3B82F6;
            margin-bottom: 2px;
        }
        .flow-step-title {
            font-size: 13px;
            font-weight: 600;
            color: #FAFAFA;
            margin-bottom: 3px;
        }
        .flow-step-desc {
            font-size: 11px;
            color: #71717A;
            line-height: 1.4;
        }
        .flow-arrow {
            text-align: center;
            font-size: 18px;
            color: #3F3F46;
            padding-top: 20px;
        }

        /* ── Glossary ────────────────────────────────────── */
        .glossary-item {
            background: transparent;
            border-bottom: 1px solid #1F1F23;
            padding: 10px 0;
        }
        .glossary-item:last-child { border-bottom: none; }
        .glossary-term {
            font-weight: 600;
            color: #FAFAFA;
            font-size: 13px;
        }
        .glossary-def {
            color: #71717A;
            font-size: 13px;
            margin-top: 2px;
            line-height: 1.5;
        }

        /* ── Compliance rows ─────────────────────────────── */
        .compliance-row {
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid #1F1F23;
            padding: 10px 0;
        }
        .compliance-row:last-child { border-bottom: none; }
        .compliance-icon { font-size: 16px; min-width: 24px; }
        .compliance-label {
            font-weight: 600;
            color: #FAFAFA;
            font-size: 13px;
            min-width: 140px;
        }
        .compliance-value {
            color: #71717A;
            font-size: 13px;
        }

        /* ── Divider ─────────────────────────────────────── */
        .section-divider {
            height: 1px;
            background: #1F1F23;
            border: none;
            margin: 22px 0;
        }

        /* ── Scrollbar ───────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #27272A; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #3F3F46; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Plotly layout ─────────────────────────────────────────────────────────── #
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color="#A1A1AA", size=12),
    title_font=dict(size=15, color="#FAFAFA"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="#1F1F23",
        borderwidth=1,
        font=dict(size=11),
    ),
    xaxis=dict(gridcolor="#1F1F23", zerolinecolor="#1F1F23"),
    yaxis=dict(gridcolor="#1F1F23", zerolinecolor="#1F1F23"),
    margin=dict(t=48, b=36, l=48, r=16),
    hoverlabel=dict(
        bgcolor="#18181B",
        bordercolor="#27272A",
        font_size=12,
        font_color="#FAFAFA",
    ),
)

CHART_COLORS = [
    "#3B82F6",  # Blue
    "#10B981",  # Emerald
    "#F59E0B",  # Amber
    "#EF4444",  # Red
    "#8B5CF6",  # Violet
    "#EC4899",  # Pink
    "#06B6D4",  # Cyan
    "#84CC16",  # Lime
]
