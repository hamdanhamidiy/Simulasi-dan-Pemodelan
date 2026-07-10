import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.data_generator import load_or_create_dataset, make_umkm_dataset
from src.simulation import (
    SCENARIOS,
    agent_status_over_time,
    build_custom_scenario,
    compute_convergence,
    format_rupiah,
    run_monte_carlo,
    run_scenarios,
    run_single_simulation,
    sensitivity_intervention,
    summarize_results,
)
from src.styles import CHART_COLORS, PLOTLY_LAYOUT, inject_custom_css

st.set_page_config(
    page_title="Dashboard ABM Kredit Mikro UMKM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()


# ── Helper: apply consistent plotly theme ──────────────────────────────────── #
def styled_layout(fig, **kwargs):
    """Apply the shared dark-glass plotly layout."""
    merged = {**PLOTLY_LAYOUT, **kwargs}
    fig.update_layout(**merged)
    return fig


# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.markdown(
    """
    <div style="text-align:center; padding: 8px 0 4px 0;">
        <span style="font-size:38px;">📊</span>
        <div style="font-size:22px; font-weight:900; letter-spacing:-0.03em; margin-top:2px; color:#E2E8F0 !important;">
            ABM UMKM
        </div>
        <div style="font-size:12px; color:#94A3B8 !important; margin-top:2px;">
            Simulasi Risiko Kredit Mikro
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

with st.sidebar.expander("⚙️ Pengaturan Simulasi", expanded=True):
    n_agents = st.slider("Jumlah agen UMKM", 100, 1000, 500, step=50,
                         help="Jumlah agen UMKM yang disimulasikan")
    n_months = st.slider("Durasi simulasi (bulan)", 12, 60, 24, step=6,
                         help="Berapa lama simulasi berjalan")
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1,
                           help="Seed untuk reproduksi hasil yang sama")
    n_monte_carlo = st.slider("Iterasi Monte Carlo", 50, 1000, 300, step=50,
                              help="Jumlah pengulangan simulasi Monte Carlo")

with st.sidebar.expander("🎯 Pilih Skenario", expanded=True):
    scenario_names = st.multiselect(
        "Skenario yang dibandingkan",
        options=list(SCENARIOS.keys()),
        default=list(SCENARIOS.keys()),
        help="Pilih satu atau lebih skenario untuk dibandingkan",
    )
    mc_scenario = st.selectbox("Skenario untuk Monte Carlo", options=list(SCENARIOS.keys()), index=2,
                               help="Skenario mana yang akan diuji dengan Monte Carlo")

with st.sidebar.expander("🧪 Skenario Custom", expanded=False):
    use_custom = st.toggle("Aktifkan skenario custom", value=False)
    custom_base = st.selectbox("Basis skenario", list(SCENARIOS.keys()), index=0)
    custom_interest = st.slider("Bunga tahunan custom", 0.03, 0.24, 0.10, step=0.01)
    custom_stressor = st.slider("Stressor ekonomi custom", 0.02, 0.22, 0.08, step=0.01)
    custom_intervention = st.slider("Kekuatan intervensi custom", 0.00, 0.30, 0.12, step=0.01)
    custom_threshold = st.slider("Ambang approval custom", 30, 85, 55, step=1)

run_button = st.sidebar.button("🚀 Jalankan / Refresh Simulasi", use_container_width=True)

st.sidebar.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
st.sidebar.markdown(
    """
    <div style="background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.15);
                border-radius: 14px; padding: 14px 16px; margin-top: 4px;">
        <div style="font-size:13px; font-weight:700; color:#A5B4FC !important; margin-bottom:6px;">
            💡 Tips
        </div>
        <div style="font-size:12px; color:#94A3B8 !important; line-height:1.5;">
            Gunakan Monte Carlo <b>1000 iterasi</b> untuk hasil akhir.
            Saat eksplorasi, 200–300 iterasi sudah cukup.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# CACHE FUNCTIONS
# =============================================================================
@st.cache_data(show_spinner=False)
def cached_dataset(n_agents: int, seed: int) -> pd.DataFrame:
    return make_umkm_dataset(n_agents=n_agents, seed=seed)


@st.cache_data(show_spinner="Menjalankan simulasi skenario...")
def cached_run_scenarios(df: pd.DataFrame, scenario_names: list[str], n_months: int, seed: int) -> dict:
    return run_scenarios(df, scenario_names, n_months=n_months, seed=seed)


@st.cache_data(show_spinner="Menjalankan Monte Carlo...")
def cached_monte_carlo(df: pd.DataFrame, scenario_name: str, n_runs: int, n_months: int, seed: int) -> pd.DataFrame:
    return run_monte_carlo(df, scenario_name, n_runs=n_runs, n_months=n_months, seed=seed)


@st.cache_data(show_spinner="Menghitung sensitivitas intervensi...")
def cached_sensitivity(df: pd.DataFrame, scenario_name: str, n_months: int, seed: int) -> pd.DataFrame:
    return sensitivity_intervention(df, scenario_name, n_runs_per_value=80, n_months=n_months, seed=seed)

# =============================================================================
# DATA & SIMULATION
# =============================================================================
if not scenario_names:
    st.warning("⚠️ Pilih minimal satu skenario pada sidebar.")
    st.stop()

df = cached_dataset(n_agents, seed)
results = cached_run_scenarios(df, scenario_names, n_months, seed)
summary_df = summarize_results(results)

if use_custom:
    custom = build_custom_scenario(
        base_name=custom_base,
        annual_interest_rate=custom_interest,
        base_stressor=custom_stressor,
        intervention_strength=custom_intervention,
        approval_threshold=custom_threshold,
    )
    monthly_custom, agents_custom = run_single_simulation(df, custom, n_months=n_months, seed=seed + 777)
    results["Custom"] = {"monthly": monthly_custom, "agents": agents_custom, "scenario": custom}
    summary_df = summarize_results(results)

# =============================================================================
# HEADER
# =============================================================================
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🏦 Dashboard Simulasi ABM<br>Risiko Kredit Mikro UMKM</div>
        <div class="hero-subtitle">
            Simulasi berbasis agen untuk menganalisis risiko gagal bayar kredit mikro UMKM
            melalui skenario <i>what-if</i>, Monte Carlo, dan analisis sensitivitas intervensi.
        </div>
        <span class="hero-badge">👤 Ahmad Hamdan Hamidiy — Pemodelan & Simulasi Data C</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# GLOBAL METRICS
# =============================================================================
best_row = summary_df.sort_values("Default Rate Akhir", ascending=True).iloc[0]
worst_row = summary_df.sort_values("Default Rate Akhir", ascending=False).iloc[0]
profit_best = summary_df.sort_values("Profit Kumulatif", ascending=False).iloc[0]
avg_approval = summary_df["Approval Rate"].mean()

m1, m2, m3, m4 = st.columns(4)
m1.metric("📋 Jumlah Agen", f"{len(df):,}".replace(",", "."),
          delta=f"{len(scenario_names)} skenario", delta_color="off")
m2.metric("✅ Default Terendah", best_row["Skenario"],
          delta=f"{best_row['Default Rate Akhir']*100:.2f}%", delta_color="inverse")
m3.metric("⚠️ Default Tertinggi", worst_row["Skenario"],
          delta=f"{worst_row['Default Rate Akhir']*100:.2f}%", delta_color="inverse")
m4.metric("💰 Profit Tertinggi", profit_best["Skenario"],
          delta=format_rupiah(profit_best["Profit Kumulatif"]), delta_color="off")

st.markdown("")  # spacer

# =============================================================================
# TABS
# =============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📌 Ringkasan",
    "🏪 Dataset UMKM",
    "📈 Simulasi What-If",
    "🎲 Monte Carlo",
    "🧠 Formulasi Model",
    "❓ Panduan & Bantuan",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — RINGKASAN
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">📌 Ringkasan Perbandingan Skenario</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Perbandingan utama antar skenario simulasi. Indikator penting: default rate akhir, '
        'approval rate, rata-rata risiko, dan profit kumulatif.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Summary table ──
    display_summary = summary_df.copy()
    display_summary["Approval Rate"] = (display_summary["Approval Rate"] * 100).map(lambda x: f"{x:.2f}%")
    display_summary["Default Rate Akhir"] = (display_summary["Default Rate Akhir"] * 100).map(lambda x: f"{x:.2f}%")
    display_summary["Rata-rata Risiko Akhir"] = display_summary["Rata-rata Risiko Akhir"].map(lambda x: f"{x:.3f}")
    display_summary["Profit Kumulatif"] = display_summary["Profit Kumulatif"].map(format_rupiah)
    st.dataframe(display_summary, use_container_width=True, hide_index=True)

    # ── Bar charts row ──
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            summary_df,
            x="Skenario",
            y="Default Rate Akhir",
            text=summary_df["Default Rate Akhir"].map(lambda x: f"{x*100:.2f}%"),
            title="Default Rate Akhir per Skenario",
            color="Skenario",
            color_discrete_sequence=CHART_COLORS,
        )
        styled_layout(fig, yaxis_tickformat=".0%", height=420)
        fig.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            summary_df,
            x="Skenario",
            y="Profit Kumulatif",
            title="Estimasi Profit Kumulatif per Skenario",
            color="Skenario",
            color_discrete_sequence=CHART_COLORS,
        )
        styled_layout(fig, height=420)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    # ── Gauge charts for best/worst ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    with g1:
        val = best_row["Default Rate Akhir"] * 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=val,
            number={"suffix": "%", "font": {"size": 32, "color": "#22C55E"}},
            title={"text": f"Default Rate Terendah — {best_row['Skenario']}", "font": {"size": 14, "color": "#94A3B8"}},
            gauge={
                "axis": {"range": [0, 50], "tickcolor": "#475569"},
                "bar": {"color": "#22C55E"},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 15], "color": "rgba(34,197,94,0.12)"},
                    {"range": [15, 30], "color": "rgba(245,158,11,0.12)"},
                    {"range": [30, 50], "color": "rgba(239,68,68,0.12)"},
                ],
                "threshold": {"line": {"color": "#22C55E", "width": 3}, "value": val},
            },
        ))
        styled_layout(fig, height=280)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        val = worst_row["Default Rate Akhir"] * 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=val,
            number={"suffix": "%", "font": {"size": 32, "color": "#EF4444"}},
            title={"text": f"Default Rate Tertinggi — {worst_row['Skenario']}", "font": {"size": 14, "color": "#94A3B8"}},
            gauge={
                "axis": {"range": [0, 50], "tickcolor": "#475569"},
                "bar": {"color": "#EF4444"},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 15], "color": "rgba(34,197,94,0.12)"},
                    {"range": [15, 30], "color": "rgba(245,158,11,0.12)"},
                    {"range": [30, 50], "color": "rgba(239,68,68,0.12)"},
                ],
                "threshold": {"line": {"color": "#EF4444", "width": 3}, "value": val},
            },
        ))
        styled_layout(fig, height=280)
        st.plotly_chart(fig, use_container_width=True)

    # ── Radar chart ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 🕸️ Radar Perbandingan Skenario")
    radar_categories = ["Approval Rate", "Default Rate Akhir", "Rata-rata Risiko Akhir"]
    fig = go.Figure()
    for i, (_, row) in enumerate(summary_df.iterrows()):
        fig.add_trace(go.Scatterpolar(
            r=[row["Approval Rate"], row["Default Rate Akhir"], row["Rata-rata Risiko Akhir"]],
            theta=radar_categories,
            fill="toself",
            name=row["Skenario"],
            line=dict(color=CHART_COLORS[i % len(CHART_COLORS)]),
            fillcolor=f"rgba({int(CHART_COLORS[i % len(CHART_COLORS)][1:3], 16)},{int(CHART_COLORS[i % len(CHART_COLORS)][3:5], 16)},{int(CHART_COLORS[i % len(CHART_COLORS)][5:7], 16)},0.08)",
        ))
    styled_layout(fig, height=440, polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=True, color="#475569", gridcolor="rgba(148,163,184,0.1)"),
        angularaxis=dict(color="#94A3B8", gridcolor="rgba(148,163,184,0.1)"),
    ))
    st.plotly_chart(fig, use_container_width=True)

    # ── Interpretation card ──
    st.markdown(
        f"""
        <div class="info-card">
            <div style="font-weight:700; color:#A5B4FC; margin-bottom:8px; font-size:15px;">
                🔍 Interpretasi Otomatis
            </div>
            <div style="color:#CBD5E1; line-height:1.7; font-size:14px;">
                Skenario dengan default rate paling rendah adalah <b style="color:#22C55E">{best_row['Skenario']}</b>
                ({best_row['Default Rate Akhir']*100:.2f}%).
                Skenario dengan default rate paling tinggi adalah <b style="color:#EF4444">{worst_row['Skenario']}</b>
                ({worst_row['Default Rate Akhir']*100:.2f}%).
                <br><br>
                Perbedaan sebesar <b>{(worst_row['Default Rate Akhir'] - best_row['Default Rate Akhir'])*100:.2f} poin persentase</b>
                menunjukkan bahwa intervensi dan seleksi kredit memiliki dampak signifikan terhadap risiko portofolio.
                Untuk pembahasan jurnal, arahkan analisis pada efektivitas intervensi, dampak stressor ekonomi,
                dan trade-off antara seleksi kredit dengan jangkauan pembiayaan UMKM.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — DATASET UMKM
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">🏪 Dataset Dummy UMKM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Setiap baris mewakili satu UMKM peminjam kredit mikro. Dataset dummy dibangun dengan aturan logis '
        'agar sesuai konteks kredit mikro Indonesia.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Stats cards ──
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("📊 Jumlah UMKM", f"{len(df):,}".replace(",", "."))
    col_b.metric("📈 Rata-rata Skor Kredit", f"{df['credit_score'].mean():.1f}")
    col_c.metric("⚡ Rata-rata Risiko Awal", f"{df['initial_risk'].mean():.3f}")
    col_d.metric("💳 Rata-rata Pinjaman", format_rupiah(df["pinjaman"].mean()))

    # ── Filters ──
    st.markdown("")
    f1, f2, f3 = st.columns([2, 3, 3])
    with f1:
        selected_sector = st.multiselect("Filter sektor", sorted(df["sektor"].unique()),
                                         default=sorted(df["sektor"].unique()))
    with f2:
        cs_range = st.slider("Range skor kredit", float(df["credit_score"].min()),
                             float(df["credit_score"].max()),
                             (float(df["credit_score"].min()), float(df["credit_score"].max())),
                             step=1.0)
    with f3:
        loan_range = st.slider("Range pinjaman (Jt)",
                               float(df["pinjaman"].min() / 1e6),
                               float(df["pinjaman"].max() / 1e6),
                               (float(df["pinjaman"].min() / 1e6), float(df["pinjaman"].max() / 1e6)),
                               step=1.0)

    filtered_df = df[
        (df["sektor"].isin(selected_sector)) &
        (df["credit_score"] >= cs_range[0]) &
        (df["credit_score"] <= cs_range[1]) &
        (df["pinjaman"] >= loan_range[0] * 1e6) &
        (df["pinjaman"] <= loan_range[1] * 1e6)
    ]

    st.markdown(f"Menampilkan **{len(filtered_df)}** dari **{len(df)}** UMKM")
    st.dataframe(filtered_df.head(30), use_container_width=True, hide_index=True)

    # Download
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Dataset (CSV)", csv_data, "dataset_umkm.csv", "text/csv",
                       use_container_width=False)

    # ── Charts row 1 ──
    c1, c2 = st.columns(2)
    with c1:
        sector_counts = filtered_df["sektor"].value_counts().reset_index()
        sector_counts.columns = ["sektor", "jumlah"]
        fig = px.pie(sector_counts, names="sektor", values="jumlah",
                     title="Komposisi Agen per Sektor", hole=0.5,
                     color_discrete_sequence=CHART_COLORS)
        styled_layout(fig, height=420)
        fig.update_traces(textinfo="percent+label", textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.histogram(filtered_df, x="credit_score", nbins=30,
                           title="Distribusi Skor Kredit",
                           color_discrete_sequence=["#6366F1"])
        styled_layout(fig, height=420)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    # ── Charts row 2 ──
    c3, c4 = st.columns(2)
    with c3:
        fig = px.box(filtered_df, x="sektor", y="initial_risk",
                     title="Risiko Awal Berdasarkan Sektor",
                     color="sektor", color_discrete_sequence=CHART_COLORS)
        styled_layout(fig, height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.scatter(
            filtered_df, x="credit_score", y="initial_risk",
            size="pinjaman", color="sektor",
            hover_data=["omzet_bulanan", "cashflow_ratio", "debt_burden"],
            title="Hubungan Skor Kredit vs Risiko Awal",
            color_discrete_sequence=CHART_COLORS,
        )
        styled_layout(fig, height=420)
        st.plotly_chart(fig, use_container_width=True)

    # ── Correlation heatmap ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 🔥 Heatmap Korelasi Antar Variabel")
    numeric_cols = ["credit_score", "initial_risk", "vulnerability", "resilience",
                    "debt_burden", "cashflow_ratio", "margin_laba", "pinjaman",
                    "omzet_bulanan", "literasi_keuangan", "digitalisasi"]
    corr = filtered_df[numeric_cols].corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto",
        color_continuous_scale=["#EF4444", "#1A1C2E", "#6366F1"],
        title="Matriks Korelasi Variabel UMKM",
    )
    styled_layout(fig, height=520)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — SIMULASI WHAT-IF
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">📈 Simulasi What-If per Bulan</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Grafik perubahan default rate, risiko, stressor, dan profit selama periode simulasi. '
        'Area chart menunjukkan tren lebih jelas dibanding line chart biasa.'
        '</div>',
        unsafe_allow_html=True,
    )

    all_monthly = []
    for name, result in results.items():
        temp = result["monthly"].copy()
        temp["Skenario"] = name
        all_monthly.append(temp)
    all_monthly_df = pd.concat(all_monthly, ignore_index=True)

    # ── Main line charts ──
    c1, c2 = st.columns(2)
    with c1:
        fig = px.area(
            all_monthly_df, x="bulan", y="default_rate", color="Skenario",
            title="📉 Perkembangan Default Rate Kumulatif",
            color_discrete_sequence=CHART_COLORS,
        )
        styled_layout(fig, yaxis_tickformat=".0%", height=430)
        fig.update_traces(line=dict(width=2.5))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.area(
            all_monthly_df, x="bulan", y="avg_risk", color="Skenario",
            title="📊 Rata-rata Risiko Agen Approved",
            color_discrete_sequence=CHART_COLORS,
        )
        styled_layout(fig, height=430)
        fig.update_traces(line=dict(width=2.5))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.area(
            all_monthly_df, x="bulan", y="cumulative_profit", color="Skenario",
            title="💰 Profit Kumulatif Portofolio Kredit",
            color_discrete_sequence=CHART_COLORS,
        )
        styled_layout(fig, height=430)
        fig.update_traces(line=dict(width=2.5))
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.line(
            all_monthly_df, x="bulan", y="stressor", color="Skenario",
            markers=True,
            title="🌊 Dinamika Stressor Ekonomi per Bulan",
            color_discrete_sequence=CHART_COLORS,
        )
        styled_layout(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)

    # ── Stacked area: active vs defaulted ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 👥 Komposisi Agen: Aktif vs Default")

    stacked_scenario = st.selectbox("Pilih skenario untuk stacked area:",
                                    list(results.keys()), key="stacked_sel")
    status_df = agent_status_over_time(results[stacked_scenario]["monthly"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=status_df["bulan"], y=status_df["active_agents"],
        mode="lines", stackgroup="one", name="Agen Aktif",
        line=dict(color="#22C55E", width=0), fillcolor="rgba(34,197,94,0.35)",
    ))
    fig.add_trace(go.Scatter(
        x=status_df["bulan"], y=status_df["defaulted_agents"],
        mode="lines", stackgroup="one", name="Agen Default",
        line=dict(color="#EF4444", width=0), fillcolor="rgba(239,68,68,0.35)",
    ))
    styled_layout(fig, height=380, title="Komposisi Agen Aktif vs Default per Bulan",
                  yaxis_title="Jumlah Agen", xaxis_title="Bulan")
    st.plotly_chart(fig, use_container_width=True)

    # ── Heatmap bulanan ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 🗺️ Heatmap Default Rate per Bulan per Skenario")
    pivot = all_monthly_df.pivot_table(index="Skenario", columns="bulan", values="default_rate")
    fig = px.imshow(
        pivot, text_auto=".1%", aspect="auto",
        color_continuous_scale=["#0F1117", "#6366F1", "#EF4444"],
        labels=dict(x="Bulan", y="Skenario", color="Default Rate"),
    )
    styled_layout(fig, height=320)
    st.plotly_chart(fig, use_container_width=True)

    # ── Scenario detail ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 📋 Detail Skenario")
    for name, result in results.items():
        st.markdown(
            f"<span class='scenario-pill'>{name}</span> "
            f"<span class='small-muted'>{result['scenario']['description']}</span>",
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — MONTE CARLO
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">🎲 Monte Carlo & Analisis Sensitivitas</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Monte Carlo menguji kestabilan hasil simulasi dengan menjalankannya berulang kali '
        'menggunakan seed berbeda. Gunakan 1000 iterasi untuk hasil akhir tugas.'
        '</div>',
        unsafe_allow_html=True,
    )

    mc_df = cached_monte_carlo(df, mc_scenario, n_monte_carlo, n_months, seed)
    mean_default = mc_df["default_rate_akhir"].mean()
    median_default = mc_df["default_rate_akhir"].median()
    std_default = mc_df["default_rate_akhir"].std()
    ci_low = mc_df["default_rate_akhir"].quantile(0.025)
    ci_high = mc_df["default_rate_akhir"].quantile(0.975)

    # ── MC metrics ──
    cm1, cm2, cm3, cm4, cm5 = st.columns(5)
    cm1.metric("🎯 Skenario MC", mc_scenario)
    cm2.metric("📊 Mean Default", f"{mean_default*100:.2f}%")
    cm3.metric("📐 Median Default", f"{median_default*100:.2f}%")
    cm4.metric("📏 Std Deviasi", f"{std_default*100:.3f}%")
    cm5.metric("🔒 CI 95%", f"{ci_low*100:.2f}% – {ci_high*100:.2f}%")

    st.markdown("")

    # ── Histogram + Violin ──
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(
            mc_df, x="default_rate_akhir", nbins=35,
            title=f"📊 Distribusi Default Rate — {mc_scenario}",
            color_discrete_sequence=["#6366F1"],
        )
        fig.add_vline(x=mean_default, line_dash="dash", line_color="#22C55E",
                      annotation_text=f"Mean: {mean_default*100:.2f}%",
                      annotation_font_color="#22C55E")
        fig.add_vline(x=ci_low, line_dash="dot", line_color="#F59E0B",
                      annotation_text="CI 2.5%", annotation_font_color="#F59E0B",
                      annotation_position="bottom left")
        fig.add_vline(x=ci_high, line_dash="dot", line_color="#F59E0B",
                      annotation_text="CI 97.5%", annotation_font_color="#F59E0B")
        styled_layout(fig, xaxis_tickformat=".0%", height=430)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure()
        fig.add_trace(go.Violin(
            y=mc_df["default_rate_akhir"], box_visible=True,
            meanline_visible=True, fillcolor="rgba(99,102,241,0.25)",
            line_color="#6366F1", name="Default Rate",
        ))
        fig.add_trace(go.Violin(
            y=mc_df["avg_risk_akhir"], box_visible=True,
            meanline_visible=True, fillcolor="rgba(34,197,94,0.25)",
            line_color="#22C55E", name="Avg Risk",
        ))
        styled_layout(fig, height=430, title="🎻 Violin Plot — Distribusi Metrik MC",
                      yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    # ── Scatter + Convergence ──
    c3, c4 = st.columns(2)
    with c3:
        fig = px.scatter(
            mc_df, x="default_rate_akhir", y="profit_kumulatif",
            title="💰 Default Rate vs Profit Kumulatif",
            color_discrete_sequence=["#8B5CF6"],
            opacity=0.6,
        )
        styled_layout(fig, xaxis_tickformat=".0%", height=430)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        conv_df = compute_convergence(mc_df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=conv_df["iterasi"], y=conv_df["upper_band"],
            mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=conv_df["iterasi"], y=conv_df["lower_band"],
            mode="lines", fill="tonexty", line=dict(width=0),
            fillcolor="rgba(99,102,241,0.12)", name="± Std Band", hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=conv_df["iterasi"], y=conv_df["cumulative_mean"],
            mode="lines", name="Cumulative Mean",
            line=dict(color="#6366F1", width=2.5),
        ))
        styled_layout(fig, height=430, title="📈 Convergence Plot — Mean Kumulatif MC",
                      xaxis_title="Iterasi", yaxis_title="Mean Default Rate",
                      yaxis_tickformat=".2%")
        st.plotly_chart(fig, use_container_width=True)

    # ── Summary statistics table ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 📋 Statistik Lengkap Monte Carlo")
    stats_data = {
        "Metrik": ["Default Rate Akhir", "Avg Risk Akhir", "Profit Kumulatif", "Total Default"],
        "Mean": [
            f"{mc_df['default_rate_akhir'].mean()*100:.3f}%",
            f"{mc_df['avg_risk_akhir'].mean():.4f}",
            format_rupiah(mc_df['profit_kumulatif'].mean()),
            f"{mc_df['total_default'].mean():.1f}",
        ],
        "Median": [
            f"{mc_df['default_rate_akhir'].median()*100:.3f}%",
            f"{mc_df['avg_risk_akhir'].median():.4f}",
            format_rupiah(mc_df['profit_kumulatif'].median()),
            f"{mc_df['total_default'].median():.0f}",
        ],
        "Std": [
            f"{mc_df['default_rate_akhir'].std()*100:.3f}%",
            f"{mc_df['avg_risk_akhir'].std():.4f}",
            format_rupiah(mc_df['profit_kumulatif'].std()),
            f"{mc_df['total_default'].std():.2f}",
        ],
        "Min": [
            f"{mc_df['default_rate_akhir'].min()*100:.3f}%",
            f"{mc_df['avg_risk_akhir'].min():.4f}",
            format_rupiah(mc_df['profit_kumulatif'].min()),
            f"{mc_df['total_default'].min():.0f}",
        ],
        "Max": [
            f"{mc_df['default_rate_akhir'].max()*100:.3f}%",
            f"{mc_df['avg_risk_akhir'].max():.4f}",
            format_rupiah(mc_df['profit_kumulatif'].max()),
            f"{mc_df['total_default'].max():.0f}",
        ],
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

    # ── Sensitivity analysis ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 🎛️ Analisis Sensitivitas Kekuatan Intervensi")

    sens_df = cached_sensitivity(df, "Intervensi KUR", n_months, seed)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sens_df["intervention_strength"],
        y=sens_df["mean_default_rate"] + sens_df["std_default_rate"],
        mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=sens_df["intervention_strength"],
        y=(sens_df["mean_default_rate"] - sens_df["std_default_rate"]).clip(lower=0),
        mode="lines", fill="tonexty", line=dict(width=0),
        fillcolor="rgba(99,102,241,0.12)", name="± Std", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=sens_df["intervention_strength"],
        y=sens_df["mean_default_rate"],
        mode="lines+markers", name="Mean Default Rate",
        line=dict(color="#6366F1", width=3),
        marker=dict(size=8, color="#6366F1"),
    ))
    styled_layout(fig,
                  title="Sensitivitas Kekuatan Intervensi terhadap Default Rate",
                  xaxis_title="Intervention Strength", yaxis_title="Mean Default Rate",
                  yaxis_tickformat=".0%", height=450)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📄 Lihat data hasil Monte Carlo"):
        st.dataframe(mc_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — FORMULASI MODEL
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">🧠 Formulasi Model ABM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Penjelasan teknis mengenai bagaimana model Agent-Based Modeling bekerja dalam simulasi ini.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Agent description card ──
    st.markdown(
        """
        <div class="glass-card">
            <div style="font-size:16px; font-weight:700; color:#A5B4FC; margin-bottom:10px;">
                🤖 Tentang Agen dalam Simulasi
            </div>
            <div style="color:#CBD5E1; line-height:1.7; font-size:14px;">
                <b>Agen</b> pada simulasi ini adalah UMKM peminjam kredit mikro. Setiap agen memiliki atribut internal
                seperti skor kredit, cashflow, agunan, debt burden, vulnerability, resilience, dan risiko awal.
                <b>Lingkungan</b> memberikan tekanan berupa stressor ekonomi yang berfluktuasi setiap bulan.
                <b>Intervensi</b> merepresentasikan kebijakan seperti KUR, subsidi bunga, pendampingan, atau seleksi kredit.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Flowchart ──
    st.markdown("#### 🔄 Alur Proses Simulasi")
    fc1, fa1, fc2, fa2, fc3, fa3, fc4 = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2])
    with fc1:
        st.markdown(
            '<div class="flow-step"><div class="flow-step-num">1</div>'
            '<div class="flow-step-title">Generate Agen</div>'
            '<div class="flow-step-desc">Buat dataset UMKM dengan atribut ekonomi</div></div>',
            unsafe_allow_html=True)
    with fa1:
        st.markdown('<div class="flow-arrow">→</div>', unsafe_allow_html=True)
    with fc2:
        st.markdown(
            '<div class="flow-step"><div class="flow-step-num">2</div>'
            '<div class="flow-step-title">Seleksi Kredit</div>'
            '<div class="flow-step-desc">Filter agen berdasarkan skor kredit</div></div>',
            unsafe_allow_html=True)
    with fa2:
        st.markdown('<div class="flow-arrow">→</div>', unsafe_allow_html=True)
    with fc3:
        st.markdown(
            '<div class="flow-step"><div class="flow-step-num">3</div>'
            '<div class="flow-step-title">Simulasi Bulanan</div>'
            '<div class="flow-step-desc">Update risiko agen setiap bulan</div></div>',
            unsafe_allow_html=True)
    with fa3:
        st.markdown('<div class="flow-arrow">→</div>', unsafe_allow_html=True)
    with fc4:
        st.markdown(
            '<div class="flow-step"><div class="flow-step-num">4</div>'
            '<div class="flow-step-title">Evaluasi Default</div>'
            '<div class="flow-step-desc">Hitung probabilitas gagal bayar</div></div>',
            unsafe_allow_html=True)

    # ── Formula ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 📐 Persamaan Transisi Risiko")
    st.markdown(
        """
        <div class="glass-card" style="text-align:center; padding:28px;">
            <div style="font-size:13px; color:#94A3B8; margin-bottom:12px; text-transform:uppercase; letter-spacing:0.08em;">
                Persamaan Utama Model
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.latex(r"Risk_{t+1}=\text{clip}\Big(0.82 \cdot Risk_t + (S_t \times V \times \alpha) + B + C - (R \times P),\ 0,\ 1\Big)")

    # ── Variable explanation ──
    st.markdown("")
    var_data = [
        ("Risk", "Risiko gagal bayar agen UMKM pada waktu t"),
        ("S (Stressor)", "Tekanan ekonomi pada bulan tertentu — berfluktuasi mengikuti pola musiman"),
        ("V (Vulnerability)", "Kerentanan agen terhadap tekanan ekonomi"),
        ("α (Sensitivity)", "Sensitivitas default berdasarkan skenario"),
        ("B (Debt Burden)", "Beban pinjaman terhadap omzet agen"),
        ("C (Contagion)", "Efek penularan dari default rate periode sebelumnya"),
        ("R (Resilience)", "Ketahanan agen — dipengaruhi cashflow, literasi, digitalisasi"),
        ("P (Intervention)", "Kekuatan intervensi kebijakan (KUR, subsidi, dll)"),
        ("clip(0,1)", "Pembatas agar risiko tetap berada pada rentang 0 sampai 1"),
    ]
    for var, desc in var_data:
        st.markdown(
            f'<div class="glossary-item">'
            f'<span class="glossary-term">{var}</span>'
            f'<div class="glossary-def">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Compliance table ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### ✅ Peta Kesesuaian dengan Ketentuan Tugas")

    compliance_items = [
        ("📐", "Pendekatan simulasi", "Agent-Based Modeling berbasis Python"),
        ("🤖", "Agen", "UMKM peminjam kredit mikro"),
        ("🌍", "Lingkungan", "Stressor ekonomi, sektor, dan contagion risk"),
        ("🛡️", "Intervensi", "KUR, pendampingan, subsidi bunga, dan seleksi kredit"),
        ("📊", "Variabel numerik", "Risk, credit score, debt burden, vulnerability, resilience"),
        ("🔄", "Aturan transisi", "Persamaan Risk(t+1) yang diperbarui per bulan"),
        ("🔀", "Skenario what-if", "Baseline, Guncangan Ekonomi, Intervensi KUR, Seleksi Kredit Ketat, Custom"),
        ("🎲", "Monte Carlo", "Dapat dijalankan hingga 1000 iterasi"),
        ("🖥️", "Dashboard", "Streamlit dengan grafik interaktif dan tabel hasil"),
    ]
    for icon, label, value in compliance_items:
        st.markdown(
            f'<div class="compliance-row">'
            f'<span class="compliance-icon">{icon}</span>'
            f'<span class="compliance-label">{label}</span>'
            f'<span style="color:#475569; margin:0 6px;">—</span>'
            f'<span class="compliance-value">{value}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — PANDUAN & BANTUAN
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.markdown('<div class="section-title">❓ Panduan & Bantuan</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Panduan lengkap cara membaca dan menggunakan dashboard ini.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Cara membaca ──
    st.markdown("#### 📖 Cara Membaca Dashboard")
    st.markdown(
        """
        <div class="info-card">
            <div style="color:#CBD5E1; line-height:1.8; font-size:14px;">
                <b style="color:#A5B4FC;">1. Ringkasan</b> — Lihat perbandingan semua skenario secara sekilas.
                Perhatikan gauge chart untuk melihat skenario terbaik dan terburuk.<br>
                <b style="color:#A5B4FC;">2. Dataset UMKM</b> — Eksplorasi data agen UMKM. Gunakan filter untuk
                menelusuri subset data tertentu.<br>
                <b style="color:#A5B4FC;">3. Simulasi What-If</b> — Amati bagaimana default rate berkembang dari waktu
                ke waktu di setiap skenario. Heatmap membantu melihat pola bulanan.<br>
                <b style="color:#A5B4FC;">4. Monte Carlo</b> — Pastikan hasil simulasi stabil dan konvergen.
                Convergence plot menunjukkan kapan rata-rata sudah stabil.<br>
                <b style="color:#A5B4FC;">5. Formulasi Model</b> — Pelajari bagaimana model bekerja secara teknis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Glossary ──
    st.markdown("#### 📚 Glosarium Istilah")
    glossary = [
        ("Default Rate", "Persentase agen yang gagal bayar dari total agen yang disetujui kreditnya."),
        ("Stressor Ekonomi", "Tekanan eksternal yang mempengaruhi risiko agen — misalnya inflasi, resesi, atau bencana."),
        ("Intervensi", "Kebijakan yang diterapkan untuk mengurangi risiko — misalnya KUR, subsidi bunga, pendampingan."),
        ("Approval Rate", "Persentase agen yang disetujui kreditnya berdasarkan ambang skor kredit."),
        ("Contagion Effect", "Efek penularan risiko — ketika banyak UMKM default, UMKM lain juga lebih berisiko."),
        ("Monte Carlo", "Metode simulasi berulang dengan variasi acak untuk menguji kestabilan hasil."),
        ("Convergence", "Titik di mana rata-rata kumulatif Monte Carlo sudah stabil dan tidak berubah signifikan."),
        ("Confidence Interval (CI)", "Rentang nilai di mana hasil sebenarnya kemungkinan berada (95% keyakinan)."),
        ("Vulnerability", "Kerentanan agen terhadap tekanan ekonomi — dipengaruhi sektor, debt burden, dan cashflow."),
        ("Resilience", "Ketahanan agen — dipengaruhi cashflow, literasi keuangan, digitalisasi, dan agunan."),
        ("Debt Burden", "Rasio beban pinjaman terhadap omzet dan tenor — semakin tinggi, semakin berisiko."),
        ("Skor Kredit", "Skor numerik yang merepresentasikan kelayakan kredit agen UMKM (0–100)."),
    ]
    for term, definition in glossary:
        st.markdown(
            f'<div class="glossary-item">'
            f'<span class="glossary-term">{term}</span>'
            f'<div class="glossary-def">{definition}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── FAQ ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 💬 Pertanyaan Umum (FAQ)")

    with st.expander("Berapa iterasi Monte Carlo yang harus saya gunakan?"):
        st.markdown(
            "Untuk eksplorasi awal, gunakan **200–300 iterasi** agar dashboard tetap responsif. "
            "Untuk hasil akhir (presentasi/jurnal), gunakan **1000 iterasi** agar hasil lebih stabil dan reliabel."
        )
    with st.expander("Apa bedanya skenario Baseline dan Intervensi KUR?"):
        st.markdown(
            "**Baseline** mensimulasikan kondisi normal tanpa kebijakan khusus. "
            "**Intervensi KUR** menambahkan subsidi bunga (bunga lebih rendah), pendampingan, "
            "dan penguatan cashflow sehingga risiko agen menjadi lebih rendah."
        )
    with st.expander("Mengapa default rate bisa berbeda setiap kali saya menjalankan?"):
        st.markdown(
            "Simulasi menggunakan komponen acak (stochastic). Untuk mendapatkan hasil yang sama, "
            "pastikan **random seed** tidak berubah. Monte Carlo membantu mengukur variasi hasil ini."
        )
    with st.expander("Apakah dataset ini asli?"):
        st.markdown(
            "Tidak. Dataset bersifat **dummy** (sintetis), dibuat menggunakan aturan logis agar "
            "sesuai konteks kredit mikro UMKM Indonesia. Fokus tugas adalah pada simulasi, bukan data."
        )
    with st.expander("Bagaimana cara menggunakan skenario custom?"):
        st.markdown(
            "Buka sidebar, aktifkan toggle **Skenario Custom**, lalu atur parameter sesuai keinginan. "
            "Skenario custom akan muncul sebagai skenario tambahan di semua tab analisis."
        )

    # ── References ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 📎 Referensi")
    st.markdown(
        """
        <div class="info-card">
            <div style="color:#CBD5E1; line-height:1.8; font-size:14px;">
                • Wilensky, U. & Rand, W. (2015). <i>An Introduction to Agent-Based Modeling</i>. MIT Press.<br>
                • Bank Indonesia — Laporan Perkembangan Kredit UMKM.<br>
                • OJK — Statistik Perbankan Indonesia.<br>
                • Streamlit Documentation — <a href="https://docs.streamlit.io" style="color:#A5B4FC;">docs.streamlit.io</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# FOOTER
# =============================================================================
st.markdown(
    """
    <div class="footer-note">
        <span style="opacity:0.7;">📊</span> Final Project Pemodelan dan Simulasi Data C —
        <b>Ahmad Hamdan Hamidiy</b> — 2025
    </div>
    """,
    unsafe_allow_html=True,
)
