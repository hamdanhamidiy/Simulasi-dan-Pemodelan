import streamlit as st


def inject_custom_css() -> None:
    """CSS tambahan agar tampilan Streamlit lebih modern dan rapi."""
    st.markdown(
        """
        <style>
        .main { background: #F8FAFC; }
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1250px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        }
        [data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            padding: 18px 18px;
            border-radius: 18px;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
        }
        .hero-card {
            background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 45%, #06B6D4 100%);
            padding: 28px 30px;
            border-radius: 26px;
            color: white;
            box-shadow: 0 18px 35px rgba(37, 99, 235, 0.20);
            margin-bottom: 20px;
        }
        .hero-title {
            font-size: 34px;
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 8px;
        }
        .hero-subtitle {
            font-size: 16px;
            opacity: 0.96;
            max-width: 900px;
        }
        .soft-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            padding: 18px 20px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.05);
            margin-bottom: 14px;
        }
        .section-title {
            font-size: 22px;
            font-weight: 800;
            color: #0F172A;
            margin: 8px 0 12px 0;
        }
        .small-muted {
            color: #64748B;
            font-size: 14px;
        }
        .scenario-pill {
            display: inline-block;
            padding: 6px 12px;
            margin: 4px 6px 4px 0;
            border-radius: 999px;
            background: #EFF6FF;
            color: #1D4ED8;
            border: 1px solid #BFDBFE;
            font-size: 13px;
            font-weight: 700;
        }
        .footer-note {
            color: #64748B;
            font-size: 13px;
            text-align: center;
            padding: 20px 0 0 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #FFFFFF;
            border-radius: 14px 14px 0 0;
            border: 1px solid #E2E8F0;
            padding: 10px 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
