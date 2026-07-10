import streamlit as st


def inject_custom_css() -> None:
    """CSS modern premium — glassmorphism, animated gradients, smooth transitions."""
    st.markdown(
        """
        <style>
        /* ── Google Font ─────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        * { font-family: 'Inter', sans-serif !important; }

        /* ── Fade-in animation ───────────────────────────── */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(18px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes gradientShift {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50%      { opacity: 0.7; }
        }
        @keyframes shimmer {
            0%   { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }

        /* ── Main canvas ─────────────────────────────────── */
        .main {
            background: linear-gradient(165deg, #0F1117 0%, #13141F 40%, #161825 100%);
        }
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1320px;
            animation: fadeInUp 0.5s ease-out;
        }

        /* ── Sidebar ─────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0D0F1A 0%, #141729 50%, #1A1E35 100%);
            border-right: 1px solid rgba(99, 102, 241, 0.15);
        }
        [data-testid="stSidebar"] * {
            color: #CBD5E1 !important;
        }
        [data-testid="stSidebar"] .stMarkdown h1 {
            color: #E2E8F0 !important;
            font-weight: 800 !important;
            letter-spacing: -0.02em;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(99, 102, 241, 0.12);
            border-radius: 16px;
            margin-bottom: 8px;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #A78BFA 100%);
            background-size: 200% 200%;
            animation: gradientShift 3s ease infinite;
            color: white !important;
            border: none;
            border-radius: 14px;
            font-weight: 700;
            font-size: 15px;
            padding: 12px 20px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 18px rgba(99, 102, 241, 0.35);
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 28px rgba(99, 102, 241, 0.5);
        }

        /* ── Metric Cards — Glassmorphism ────────────────── */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(99, 102, 241, 0.12);
            padding: 20px 20px;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInUp 0.6s ease-out;
        }
        div[data-testid="stMetric"]:hover {
            border-color: rgba(99, 102, 241, 0.35);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.12);
            transform: translateY(-3px);
        }
        div[data-testid="stMetric"] label {
            color: #94A3B8 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #F1F5F9 !important;
            font-weight: 800 !important;
            font-size: 22px !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            font-weight: 600 !important;
        }

        /* ── Hero Card ───────────────────────────────────── */
        .hero-card {
            background: linear-gradient(135deg, #4F46E5 0%, #6366F1 25%, #8B5CF6 50%, #A78BFA 75%, #6366F1 100%);
            background-size: 300% 300%;
            animation: gradientShift 6s ease infinite;
            padding: 36px 38px;
            border-radius: 28px;
            color: white;
            box-shadow: 0 20px 50px rgba(99, 102, 241, 0.25),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }
        .hero-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
            border-radius: 50%;
        }
        .hero-card::after {
            content: '';
            position: absolute;
            bottom: -30%;
            left: -10%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
            border-radius: 50%;
        }
        .hero-title {
            font-size: 32px;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 10px;
            letter-spacing: -0.03em;
            position: relative;
            z-index: 1;
        }
        .hero-subtitle {
            font-size: 15px;
            opacity: 0.92;
            max-width: 820px;
            line-height: 1.55;
            position: relative;
            z-index: 1;
        }
        .hero-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 5px 14px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 12px;
            position: relative;
            z-index: 1;
        }

        /* ── Glass Card ──────────────────────────────────── */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(99, 102, 241, 0.1);
            padding: 22px 24px;
            border-radius: 22px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            margin-bottom: 16px;
            transition: all 0.35s ease;
            animation: fadeInUp 0.6s ease-out;
        }
        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.25);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.08);
        }

        /* ── Info Card (with colored left border) ────────── */
        .info-card {
            background: rgba(99, 102, 241, 0.06);
            border-left: 4px solid #6366F1;
            padding: 18px 22px;
            border-radius: 0 16px 16px 0;
            margin: 12px 0;
            animation: fadeInUp 0.5s ease-out;
        }
        .info-card-success {
            background: rgba(34, 197, 94, 0.06);
            border-left: 4px solid #22C55E;
            padding: 18px 22px;
            border-radius: 0 16px 16px 0;
            margin: 12px 0;
        }
        .info-card-warning {
            background: rgba(245, 158, 11, 0.06);
            border-left: 4px solid #F59E0B;
            padding: 18px 22px;
            border-radius: 0 16px 16px 0;
            margin: 12px 0;
        }
        .info-card-danger {
            background: rgba(239, 68, 68, 0.06);
            border-left: 4px solid #EF4444;
            padding: 18px 22px;
            border-radius: 0 16px 16px 0;
            margin: 12px 0;
        }

        /* ── Section Titles ──────────────────────────────── */
        .section-title {
            font-size: 24px;
            font-weight: 800;
            color: #F1F5F9;
            margin: 8px 0 6px 0;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .section-desc {
            color: #94A3B8;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 18px;
        }

        /* ── Scenario Pill ───────────────────────────────── */
        .scenario-pill {
            display: inline-block;
            padding: 7px 16px;
            margin: 4px 6px 4px 0;
            border-radius: 999px;
            background: rgba(99, 102, 241, 0.12);
            color: #A5B4FC !important;
            border: 1px solid rgba(99, 102, 241, 0.25);
            font-size: 13px;
            font-weight: 700;
            transition: all 0.25s ease;
        }
        .scenario-pill:hover {
            background: rgba(99, 102, 241, 0.22);
            transform: scale(1.03);
        }
        .small-muted {
            color: #64748B;
            font-size: 14px;
        }

        /* ── Footer ──────────────────────────────────────── */
        .footer-note {
            color: #475569;
            font-size: 13px;
            text-align: center;
            padding: 28px 0 8px 0;
            border-top: 1px solid rgba(99, 102, 241, 0.08);
            margin-top: 30px;
        }

        /* ── Tabs ────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 16px;
            padding: 4px;
            border: 1px solid rgba(99, 102, 241, 0.08);
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 12px;
            border: none;
            padding: 10px 20px;
            color: #94A3B8 !important;
            font-weight: 600;
            transition: all 0.25s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(99, 102, 241, 0.08);
            color: #C7D2FE !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(99, 102, 241, 0.15) !important;
            color: #A5B4FC !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #6366F1 !important;
            border-radius: 12px;
        }

        /* ── Dataframe ───────────────────────────────────── */
        [data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(99, 102, 241, 0.1);
        }

        /* ── Expander ────────────────────────────────────── */
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.03) !important;
            border-radius: 14px !important;
            border: 1px solid rgba(99, 102, 241, 0.1) !important;
            font-weight: 600 !important;
        }

        /* ── Download button ─────────────────────────────── */
        .stDownloadButton > button {
            background: rgba(99, 102, 241, 0.12) !important;
            border: 1px solid rgba(99, 102, 241, 0.25) !important;
            color: #A5B4FC !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        .stDownloadButton > button:hover {
            background: rgba(99, 102, 241, 0.22) !important;
            transform: translateY(-1px) !important;
        }

        /* ── Flowchart cards ─────────────────────────────── */
        .flow-step {
            background: rgba(99, 102, 241, 0.06);
            border: 1px solid rgba(99, 102, 241, 0.15);
            border-radius: 16px;
            padding: 16px 18px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .flow-step:hover {
            border-color: rgba(99, 102, 241, 0.35);
            transform: translateY(-2px);
        }
        .flow-step-num {
            font-size: 28px;
            font-weight: 900;
            color: #6366F1;
            margin-bottom: 4px;
        }
        .flow-step-title {
            font-size: 14px;
            font-weight: 700;
            color: #E2E8F0;
            margin-bottom: 4px;
        }
        .flow-step-desc {
            font-size: 12px;
            color: #94A3B8;
            line-height: 1.4;
        }
        .flow-arrow {
            text-align: center;
            font-size: 24px;
            color: #6366F1;
            padding-top: 22px;
        }

        /* ── Glossary cards ──────────────────────────────── */
        .glossary-item {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(99, 102, 241, 0.1);
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 8px;
            transition: all 0.25s ease;
        }
        .glossary-item:hover {
            border-color: rgba(99, 102, 241, 0.3);
        }
        .glossary-term {
            font-weight: 700;
            color: #A5B4FC;
            font-size: 14px;
        }
        .glossary-def {
            color: #94A3B8;
            font-size: 13px;
            margin-top: 4px;
            line-height: 1.5;
        }

        /* ── Compliance row ──────────────────────────────── */
        .compliance-row {
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(99, 102, 241, 0.08);
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 6px;
            transition: all 0.2s ease;
        }
        .compliance-row:hover {
            background: rgba(99, 102, 241, 0.05);
        }
        .compliance-icon {
            font-size: 20px;
            min-width: 28px;
        }
        .compliance-label {
            font-weight: 600;
            color: #E2E8F0;
            font-size: 14px;
        }
        .compliance-value {
            color: #94A3B8;
            font-size: 13px;
        }

        /* ── Divider ─────────────────────────────────────── */
        .gradient-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
            border: none;
            margin: 20px 0;
        }

        /* ── Scrollbar ───────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.3);
            border-radius: 999px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.5);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Plotly template for dark themed charts ────────────────────────────────── #
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#CBD5E1"),
    title_font=dict(size=17, color="#F1F5F9"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(99,102,241,0.12)",
        borderwidth=1,
        font=dict(size=12),
    ),
    xaxis=dict(gridcolor="rgba(148,163,184,0.08)", zerolinecolor="rgba(148,163,184,0.08)"),
    yaxis=dict(gridcolor="rgba(148,163,184,0.08)", zerolinecolor="rgba(148,163,184,0.08)"),
    margin=dict(t=50, b=40, l=50, r=20),
    hoverlabel=dict(
        bgcolor="#1E1E2E",
        bordercolor="rgba(99,102,241,0.3)",
        font_size=13,
        font_color="#E2E8F0",
    ),
)

# Curated color palette for chart traces
CHART_COLORS = [
    "#6366F1",  # Indigo
    "#22C55E",  # Green
    "#F59E0B",  # Amber
    "#EF4444",  # Red
    "#06B6D4",  # Cyan
    "#EC4899",  # Pink
    "#8B5CF6",  # Violet
    "#14B8A6",  # Teal
]
