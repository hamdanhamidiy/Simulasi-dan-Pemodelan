from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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


def styled(fig, **kw):
    fig.update_layout(**{**PLOTLY_LAYOUT, **kw})
    return fig


# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.markdown("# ABM UMKM")
st.sidebar.caption("Simulasi risiko kredit mikro UMKM")

with st.sidebar.expander("Pengaturan Simulasi", expanded=True):
    n_agents = st.slider("Jumlah agen UMKM", 100, 1000, 500, step=50)
    n_months = st.slider("Durasi simulasi (bulan)", 12, 60, 24, step=6)
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
    n_monte_carlo = st.slider("Iterasi Monte Carlo", 50, 1000, 300, step=50)

with st.sidebar.expander("Pilih Skenario", expanded=True):
    scenario_names = st.multiselect(
        "Skenario yang dibandingkan",
        options=list(SCENARIOS.keys()),
        default=list(SCENARIOS.keys()),
    )
    mc_scenario = st.selectbox("Skenario untuk Monte Carlo", options=list(SCENARIOS.keys()), index=2)

with st.sidebar.expander("Skenario Custom", expanded=False):
    use_custom = st.toggle("Aktifkan skenario custom", value=False)
    custom_base = st.selectbox("Basis skenario", list(SCENARIOS.keys()), index=0)
    custom_interest = st.slider("Bunga tahunan custom", 0.03, 0.24, 0.10, step=0.01)
    custom_stressor = st.slider("Stressor ekonomi custom", 0.02, 0.22, 0.08, step=0.01)
    custom_intervention = st.slider("Kekuatan intervensi custom", 0.00, 0.30, 0.12, step=0.01)
    custom_threshold = st.slider("Ambang approval custom", 30, 85, 55, step=1)

run_button = st.sidebar.button("Jalankan Simulasi", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "Gunakan Monte Carlo **1000 iterasi** untuk hasil akhir. "
    "Untuk eksplorasi, 200–300 iterasi sudah cukup."
)

# =============================================================================
# CACHE
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
    st.warning("Pilih minimal satu skenario pada sidebar.")
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
        <div class="hero-title">Dashboard Simulasi ABM — Risiko Kredit Mikro UMKM</div>
        <div class="hero-subtitle">
            Simulasi berbasis agen untuk menganalisis risiko gagal bayar kredit mikro UMKM
            melalui skenario what-if, Monte Carlo, dan analisis sensitivitas intervensi.
        </div>
        <span class="hero-badge">Ahmad Hamdan Hamidiy · Pemodelan & Simulasi Data C</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# GLOBAL METRICS
# =============================================================================
best = summary_df.sort_values("Default Rate Akhir").iloc[0]
worst = summary_df.sort_values("Default Rate Akhir").iloc[-1]
profit_best = summary_df.sort_values("Profit Kumulatif").iloc[-1]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Jumlah Agen", f"{len(df):,}".replace(",", "."))
m2.metric("Default Terendah", best["Skenario"], f"{best['Default Rate Akhir']*100:.2f}%")
m3.metric("Default Tertinggi", worst["Skenario"], f"{worst['Default Rate Akhir']*100:.2f}%")
m4.metric("Profit Tertinggi", profit_best["Skenario"], format_rupiah(profit_best["Profit Kumulatif"]))

st.markdown("")

# =============================================================================
# TABS
# =============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Ringkasan",
    "Dataset UMKM",
    "Simulasi What-If",
    "Monte Carlo",
    "Formulasi Model",
    "Panduan",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — RINGKASAN
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Ringkasan Perbandingan Skenario</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Perbandingan indikator utama antar skenario: default rate akhir, approval rate, '
        'rata-rata risiko, dan profit kumulatif.'
        '</div>',
        unsafe_allow_html=True,
    )

    display_summary = summary_df.copy()
    display_summary["Approval Rate"] = (display_summary["Approval Rate"] * 100).map(lambda x: f"{x:.2f}%")
    display_summary["Default Rate Akhir"] = (display_summary["Default Rate Akhir"] * 100).map(lambda x: f"{x:.2f}%")
    display_summary["Rata-rata Risiko Akhir"] = display_summary["Rata-rata Risiko Akhir"].map(lambda x: f"{x:.3f}")
    display_summary["Profit Kumulatif"] = display_summary["Profit Kumulatif"].map(format_rupiah)
    st.dataframe(display_summary, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            summary_df, x="Skenario", y="Default Rate Akhir",
            text=summary_df["Default Rate Akhir"].map(lambda x: f"{x*100:.2f}%"),
            title="Default Rate Akhir per Skenario",
            color="Skenario", color_discrete_sequence=CHART_COLORS,
        )
        styled(fig, yaxis_tickformat=".0%", height=420, showlegend=False)
        fig.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            summary_df, x="Skenario", y="Profit Kumulatif",
            title="Profit Kumulatif per Skenario",
            color="Skenario", color_discrete_sequence=CHART_COLORS,
        )
        styled(fig, height=420, showlegend=False)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    # Gauge
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    with g1:
        val = best["Default Rate Akhir"] * 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={"suffix": "%", "font": {"size": 28, "color": "#10B981"}},
            title={"text": f"Default Terendah — {best['Skenario']}", "font": {"size": 13, "color": "#71717A"}},
            gauge=dict(
                axis=dict(range=[0, 50], tickcolor="#3F3F46"),
                bar=dict(color="#10B981"),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
                steps=[
                    dict(range=[0, 15], color="#052E16"),
                    dict(range=[15, 30], color="#1C1917"),
                    dict(range=[30, 50], color="#1C1012"),
                ],
            ),
        ))
        styled(fig, height=260)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        val = worst["Default Rate Akhir"] * 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={"suffix": "%", "font": {"size": 28, "color": "#EF4444"}},
            title={"text": f"Default Tertinggi — {worst['Skenario']}", "font": {"size": 13, "color": "#71717A"}},
            gauge=dict(
                axis=dict(range=[0, 50], tickcolor="#3F3F46"),
                bar=dict(color="#EF4444"),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
                steps=[
                    dict(range=[0, 15], color="#052E16"),
                    dict(range=[15, 30], color="#1C1917"),
                    dict(range=[30, 50], color="#1C1012"),
                ],
            ),
        ))
        styled(fig, height=260)
        st.plotly_chart(fig, use_container_width=True)

    # Radar
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Perbandingan Radar Antar Skenario**")
    cats = ["Approval Rate", "Default Rate Akhir", "Rata-rata Risiko Akhir"]
    fig = go.Figure()
    for i, (_, row) in enumerate(summary_df.iterrows()):
        c = CHART_COLORS[i % len(CHART_COLORS)]
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        fig.add_trace(go.Scatterpolar(
            r=[row["Approval Rate"], row["Default Rate Akhir"], row["Rata-rata Risiko Akhir"]],
            theta=cats, fill="toself", name=row["Skenario"],
            line=dict(color=c), fillcolor=f"rgba({r},{g},{b},0.06)",
        ))
    styled(fig, height=420, polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=True, color="#3F3F46", gridcolor="#1F1F23"),
        angularaxis=dict(color="#71717A", gridcolor="#1F1F23"),
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Interpretation
    diff_pct = (worst["Default Rate Akhir"] - best["Default Rate Akhir"]) * 100
    st.markdown(
        f"""
        <div class="info-card">
            <div style="font-weight:600; color:#FAFAFA; margin-bottom:6px; font-size:14px;">Interpretasi</div>
            <div style="color:#A1A1AA; line-height:1.7; font-size:13px;">
                Skenario dengan default rate paling rendah adalah <b style="color:#10B981">{best['Skenario']}</b>
                ({best['Default Rate Akhir']*100:.2f}%), sedangkan yang tertinggi adalah
                <b style="color:#EF4444">{worst['Skenario']}</b> ({worst['Default Rate Akhir']*100:.2f}%).
                Perbedaan sebesar {diff_pct:.2f} poin persentase menunjukkan bahwa intervensi dan seleksi kredit
                berdampak signifikan terhadap risiko portofolio. Analisis dapat diarahkan pada efektivitas intervensi,
                dampak stressor, dan trade-off antara seleksi kredit dengan jangkauan pembiayaan.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — DATASET
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Dataset UMKM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Dataset sintetis yang mewakili agen UMKM peminjam kredit mikro. Dibangun dengan aturan logis '
        'agar sesuai konteks kredit mikro Indonesia.'
        '</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Jumlah UMKM", f"{len(df):,}".replace(",", "."))
    col_b.metric("Rata-rata Skor Kredit", f"{df['credit_score'].mean():.1f}")
    col_c.metric("Rata-rata Risiko Awal", f"{df['initial_risk'].mean():.3f}")
    col_d.metric("Rata-rata Pinjaman", format_rupiah(df["pinjaman"].mean()))

    st.markdown("")
    f1, f2, f3 = st.columns([2, 3, 3])
    with f1:
        selected_sector = st.multiselect("Sektor", sorted(df["sektor"].unique()),
                                         default=sorted(df["sektor"].unique()))
    with f2:
        cs_range = st.slider("Skor kredit",
                             float(df["credit_score"].min()), float(df["credit_score"].max()),
                             (float(df["credit_score"].min()), float(df["credit_score"].max())), step=1.0)
    with f3:
        loan_range = st.slider("Pinjaman (Jt)",
                               float(df["pinjaman"].min() / 1e6), float(df["pinjaman"].max() / 1e6),
                               (float(df["pinjaman"].min() / 1e6), float(df["pinjaman"].max() / 1e6)), step=1.0)

    filtered = df[
        (df["sektor"].isin(selected_sector)) &
        (df["credit_score"].between(cs_range[0], cs_range[1])) &
        (df["pinjaman"].between(loan_range[0] * 1e6, loan_range[1] * 1e6))
    ]

    st.caption(f"Menampilkan {len(filtered)} dari {len(df)} data")
    st.dataframe(filtered.head(30), use_container_width=True, hide_index=True)

    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv_data, "dataset_umkm.csv", "text/csv")

    c1, c2 = st.columns(2)
    with c1:
        sector_counts = filtered["sektor"].value_counts().reset_index()
        sector_counts.columns = ["sektor", "jumlah"]
        fig = px.pie(sector_counts, names="sektor", values="jumlah",
                     title="Komposisi Agen per Sektor", hole=0.5,
                     color_discrete_sequence=CHART_COLORS)
        styled(fig, height=400)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(filtered, x="credit_score", nbins=30,
                           title="Distribusi Skor Kredit",
                           color_discrete_sequence=["#3B82F6"])
        styled(fig, height=400)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.box(filtered, x="sektor", y="initial_risk",
                     title="Risiko Awal per Sektor",
                     color="sektor", color_discrete_sequence=CHART_COLORS)
        styled(fig, height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.scatter(filtered, x="credit_score", y="initial_risk",
                         size="pinjaman", color="sektor",
                         hover_data=["omzet_bulanan", "cashflow_ratio", "debt_burden"],
                         title="Skor Kredit vs Risiko Awal",
                         color_discrete_sequence=CHART_COLORS)
        styled(fig, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Korelasi Antar Variabel**")
    num_cols = ["credit_score", "initial_risk", "vulnerability", "resilience",
                "debt_burden", "cashflow_ratio", "margin_laba", "pinjaman",
                "omzet_bulanan", "literasi_keuangan", "digitalisasi"]
    corr = filtered[num_cols].corr()
    fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                    color_continuous_scale=["#EF4444", "#0A0A0B", "#3B82F6"],
                    title="Matriks Korelasi")
    styled(fig, height=500)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — SIMULASI WHAT-IF
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Simulasi What-If</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Perubahan default rate, risiko, stressor, dan profit portofolio selama periode simulasi.'
        '</div>',
        unsafe_allow_html=True,
    )

    all_monthly = []
    for name, result in results.items():
        temp = result["monthly"].copy()
        temp["Skenario"] = name
        all_monthly.append(temp)
    all_monthly_df = pd.concat(all_monthly, ignore_index=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(all_monthly_df, x="bulan", y="default_rate", color="Skenario",
                      title="Default Rate Kumulatif", color_discrete_sequence=CHART_COLORS)
        styled(fig, yaxis_tickformat=".0%", height=400)
        fig.update_traces(line_width=2)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(all_monthly_df, x="bulan", y="avg_risk", color="Skenario",
                      title="Rata-rata Risiko Agen Approved", color_discrete_sequence=CHART_COLORS)
        styled(fig, height=400)
        fig.update_traces(line_width=2)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.line(all_monthly_df, x="bulan", y="cumulative_profit", color="Skenario",
                      title="Profit Kumulatif Portofolio", color_discrete_sequence=CHART_COLORS)
        styled(fig, height=400)
        fig.update_traces(line_width=2)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.line(all_monthly_df, x="bulan", y="stressor", color="Skenario",
                      markers=True, title="Stressor Ekonomi per Bulan",
                      color_discrete_sequence=CHART_COLORS)
        styled(fig, height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Stacked area
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Komposisi Agen: Aktif vs Default**")
    stacked_sel = st.selectbox("Skenario", list(results.keys()), key="stack_sel")
    status_df = agent_status_over_time(results[stacked_sel]["monthly"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=status_df["bulan"], y=status_df["active_agents"],
        mode="lines", stackgroup="one", name="Aktif",
        line=dict(color="#10B981", width=0), fillcolor="rgba(16,185,129,0.3)",
    ))
    fig.add_trace(go.Scatter(
        x=status_df["bulan"], y=status_df["defaulted_agents"],
        mode="lines", stackgroup="one", name="Default",
        line=dict(color="#EF4444", width=0), fillcolor="rgba(239,68,68,0.3)",
    ))
    styled(fig, height=350, yaxis_title="Jumlah Agen", xaxis_title="Bulan")
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Heatmap Default Rate**")
    pivot = all_monthly_df.pivot_table(index="Skenario", columns="bulan", values="default_rate")
    fig = px.imshow(pivot, text_auto=".1%", aspect="auto",
                    color_continuous_scale=["#0A0A0B", "#3B82F6", "#EF4444"],
                    labels=dict(x="Bulan", y="Skenario", color="Default Rate"))
    styled(fig, height=300)
    st.plotly_chart(fig, use_container_width=True)

    # Detail
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Detail Skenario**")
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
    st.markdown('<div class="section-title">Monte Carlo & Sensitivitas</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Monte Carlo menguji kestabilan hasil dengan menjalankan simulasi berulang kali. '
        'Gunakan 1000 iterasi untuk hasil akhir.'
        '</div>',
        unsafe_allow_html=True,
    )

    mc_df = cached_monte_carlo(df, mc_scenario, n_monte_carlo, n_months, seed)
    mean_def = mc_df["default_rate_akhir"].mean()
    median_def = mc_df["default_rate_akhir"].median()
    std_def = mc_df["default_rate_akhir"].std()
    ci_lo = mc_df["default_rate_akhir"].quantile(0.025)
    ci_hi = mc_df["default_rate_akhir"].quantile(0.975)

    cm1, cm2, cm3, cm4 = st.columns(4)
    cm1.metric("Skenario", mc_scenario)
    cm2.metric("Mean Default", f"{mean_def*100:.2f}%")
    cm3.metric("Std Deviasi", f"{std_def*100:.3f}%")
    cm4.metric("CI 95%", f"{ci_lo*100:.2f}% – {ci_hi*100:.2f}%")

    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(mc_df, x="default_rate_akhir", nbins=35,
                           title=f"Distribusi Default Rate — {mc_scenario}",
                           color_discrete_sequence=["#3B82F6"])
        fig.add_vline(x=mean_def, line_dash="dash", line_color="#10B981",
                      annotation_text=f"Mean {mean_def*100:.2f}%",
                      annotation_font_color="#10B981")
        styled(fig, xaxis_tickformat=".0%", height=400)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure()
        fig.add_trace(go.Violin(
            y=mc_df["default_rate_akhir"], box_visible=True, meanline_visible=True,
            fillcolor="rgba(59,130,246,0.15)", line_color="#3B82F6", name="Default Rate",
        ))
        fig.add_trace(go.Violin(
            y=mc_df["avg_risk_akhir"], box_visible=True, meanline_visible=True,
            fillcolor="rgba(16,185,129,0.15)", line_color="#10B981", name="Avg Risk",
        ))
        styled(fig, height=400, title="Distribusi Metrik MC", yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.scatter(mc_df, x="default_rate_akhir", y="profit_kumulatif",
                         title="Default Rate vs Profit",
                         color_discrete_sequence=["#8B5CF6"], opacity=0.5)
        styled(fig, xaxis_tickformat=".0%", height=400)
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
            fillcolor="rgba(59,130,246,0.08)", name="± Std", hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=conv_df["iterasi"], y=conv_df["cumulative_mean"],
            mode="lines", name="Cumulative Mean", line=dict(color="#3B82F6", width=2),
        ))
        styled(fig, height=400, title="Convergence Plot",
               xaxis_title="Iterasi", yaxis_title="Mean Default Rate", yaxis_tickformat=".2%")
        st.plotly_chart(fig, use_container_width=True)

    # Stats table
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Statistik Monte Carlo**")
    stats = pd.DataFrame({
        "Metrik": ["Default Rate Akhir", "Avg Risk Akhir", "Profit Kumulatif", "Total Default"],
        "Mean": [f"{mc_df['default_rate_akhir'].mean()*100:.3f}%", f"{mc_df['avg_risk_akhir'].mean():.4f}",
                 format_rupiah(mc_df['profit_kumulatif'].mean()), f"{mc_df['total_default'].mean():.1f}"],
        "Median": [f"{mc_df['default_rate_akhir'].median()*100:.3f}%", f"{mc_df['avg_risk_akhir'].median():.4f}",
                   format_rupiah(mc_df['profit_kumulatif'].median()), f"{mc_df['total_default'].median():.0f}"],
        "Std": [f"{mc_df['default_rate_akhir'].std()*100:.3f}%", f"{mc_df['avg_risk_akhir'].std():.4f}",
                format_rupiah(mc_df['profit_kumulatif'].std()), f"{mc_df['total_default'].std():.2f}"],
        "Min": [f"{mc_df['default_rate_akhir'].min()*100:.3f}%", f"{mc_df['avg_risk_akhir'].min():.4f}",
                format_rupiah(mc_df['profit_kumulatif'].min()), f"{int(mc_df['total_default'].min())}"],
        "Max": [f"{mc_df['default_rate_akhir'].max()*100:.3f}%", f"{mc_df['avg_risk_akhir'].max():.4f}",
                format_rupiah(mc_df['profit_kumulatif'].max()), f"{int(mc_df['total_default'].max())}"],
    })
    st.dataframe(stats, use_container_width=True, hide_index=True)

    # Sensitivity
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Sensitivitas Kekuatan Intervensi**")
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
        fillcolor="rgba(59,130,246,0.08)", name="± Std", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=sens_df["intervention_strength"], y=sens_df["mean_default_rate"],
        mode="lines+markers", name="Mean Default Rate",
        line=dict(color="#3B82F6", width=2), marker=dict(size=6),
    ))
    styled(fig, xaxis_title="Intervention Strength", yaxis_title="Mean Default Rate",
           yaxis_tickformat=".0%", height=420)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Lihat data Monte Carlo"):
        st.dataframe(mc_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — FORMULASI MODEL
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">Formulasi Model ABM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Penjelasan teknis model Agent-Based Modeling yang digunakan dalam simulasi ini.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="glass-card">
            <div style="font-weight:600; color:#FAFAFA; margin-bottom:8px; font-size:14px;">
                Tentang Agen
            </div>
            <div style="color:#A1A1AA; line-height:1.7; font-size:13px;">
                Agen pada simulasi ini adalah UMKM peminjam kredit mikro. Setiap agen memiliki atribut internal
                seperti skor kredit, cashflow, agunan, debt burden, vulnerability, resilience, dan risiko awal.
                Lingkungan memberikan tekanan berupa stressor ekonomi yang berfluktuasi setiap bulan.
                Intervensi merepresentasikan kebijakan seperti KUR, subsidi bunga, pendampingan, atau seleksi kredit.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Flowchart
    st.markdown("**Alur Proses Simulasi**")
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
            '<div class="flow-step-desc">Update risiko agen per bulan</div></div>',
            unsafe_allow_html=True)
    with fa3:
        st.markdown('<div class="flow-arrow">→</div>', unsafe_allow_html=True)
    with fc4:
        st.markdown(
            '<div class="flow-step"><div class="flow-step-num">4</div>'
            '<div class="flow-step-title">Evaluasi Default</div>'
            '<div class="flow-step-desc">Hitung probabilitas gagal bayar</div></div>',
            unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Persamaan Transisi Risiko**")
    st.latex(r"Risk_{t+1}=\text{clip}\Big(0.82 \cdot Risk_t + (S_t \times V \times \alpha) + B + C - (R \times P),\ 0,\ 1\Big)")

    st.markdown("")
    variables = [
        ("Risk", "Risiko gagal bayar agen UMKM pada waktu t"),
        ("S (Stressor)", "Tekanan ekonomi pada bulan tertentu, berfluktuasi mengikuti pola musiman"),
        ("V (Vulnerability)", "Kerentanan agen terhadap tekanan ekonomi"),
        ("α (Sensitivity)", "Sensitivitas default berdasarkan skenario"),
        ("B (Debt Burden)", "Beban pinjaman terhadap omzet agen"),
        ("C (Contagion)", "Efek penularan dari default rate periode sebelumnya"),
        ("R (Resilience)", "Ketahanan agen, dipengaruhi cashflow, literasi, digitalisasi"),
        ("P (Intervention)", "Kekuatan intervensi kebijakan"),
    ]
    for var, desc in variables:
        st.markdown(
            f'<div class="glossary-item">'
            f'<span class="glossary-term">{var}</span>'
            f'<div class="glossary-def">{desc}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Kesesuaian dengan Ketentuan Tugas**")
    items = [
        ("Pendekatan simulasi", "Agent-Based Modeling berbasis Python"),
        ("Agen", "UMKM peminjam kredit mikro"),
        ("Lingkungan", "Stressor ekonomi, sektor, dan contagion risk"),
        ("Intervensi", "KUR, pendampingan, subsidi bunga, dan seleksi kredit"),
        ("Variabel numerik", "Risk, credit score, debt burden, vulnerability, resilience"),
        ("Aturan transisi", "Persamaan Risk(t+1) yang diperbarui per bulan"),
        ("Skenario what-if", "Baseline, Guncangan Ekonomi, Intervensi KUR, Seleksi Kredit Ketat, Custom"),
        ("Monte Carlo", "Dapat dijalankan hingga 1000 iterasi"),
        ("Dashboard", "Streamlit dengan grafik interaktif dan tabel hasil"),
    ]
    for label, value in items:
        st.markdown(
            f'<div class="compliance-row">'
            f'<span class="compliance-label">{label}</span>'
            f'<span style="color:#3F3F46;">—</span>'
            f'<span class="compliance-value">{value}</span></div>',
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — PANDUAN
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.markdown('<div class="section-title">Panduan Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">'
        'Panduan cara membaca dan menggunakan dashboard ini.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Cara Membaca Dashboard**")
    st.markdown(
        """
        <div class="info-card">
            <div style="color:#A1A1AA; line-height:1.8; font-size:13px;">
                <b style="color:#FAFAFA;">Ringkasan</b> — Lihat perbandingan semua skenario secara sekilas.
                Gauge chart menunjukkan skenario terbaik dan terburuk.<br><br>
                <b style="color:#FAFAFA;">Dataset UMKM</b> — Eksplorasi data agen UMKM.
                Gunakan filter untuk menelusuri subset tertentu.<br><br>
                <b style="color:#FAFAFA;">Simulasi What-If</b> — Amati perkembangan default rate dari waktu ke waktu.
                Heatmap membantu melihat pola bulanan.<br><br>
                <b style="color:#FAFAFA;">Monte Carlo</b> — Pastikan hasil stabil dan konvergen.
                Convergence plot menunjukkan kapan rata-rata sudah stabil.<br><br>
                <b style="color:#FAFAFA;">Formulasi Model</b> — Pelajari cara kerja model secara teknis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Glosarium**")
    glossary = [
        ("Default Rate", "Persentase agen yang gagal bayar dari total agen yang disetujui kreditnya."),
        ("Stressor Ekonomi", "Tekanan eksternal yang mempengaruhi risiko agen, misalnya inflasi atau resesi."),
        ("Intervensi", "Kebijakan yang diterapkan untuk mengurangi risiko, misalnya KUR atau subsidi bunga."),
        ("Approval Rate", "Persentase agen yang disetujui kreditnya berdasarkan ambang skor kredit."),
        ("Contagion Effect", "Efek penularan risiko — ketika banyak UMKM default, UMKM lain juga lebih berisiko."),
        ("Monte Carlo", "Metode simulasi berulang dengan variasi acak untuk menguji kestabilan hasil."),
        ("Convergence", "Titik di mana rata-rata kumulatif sudah stabil dan tidak berubah signifikan."),
        ("Confidence Interval", "Rentang nilai di mana hasil sebenarnya kemungkinan berada (95% keyakinan)."),
        ("Vulnerability", "Kerentanan agen terhadap tekanan ekonomi."),
        ("Resilience", "Ketahanan agen, dipengaruhi cashflow, literasi keuangan, digitalisasi, dan agunan."),
        ("Debt Burden", "Rasio beban pinjaman terhadap omzet dan tenor."),
        ("Skor Kredit", "Skor numerik yang merepresentasikan kelayakan kredit agen UMKM (0–100)."),
    ]
    for term, defn in glossary:
        st.markdown(
            f'<div class="glossary-item">'
            f'<span class="glossary-term">{term}</span>'
            f'<div class="glossary-def">{defn}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**FAQ**")

    with st.expander("Berapa iterasi Monte Carlo yang ideal?"):
        st.write("Untuk eksplorasi awal, 200–300 iterasi sudah cukup. Untuk hasil akhir presentasi atau jurnal, gunakan 1000 iterasi.")

    with st.expander("Apa bedanya Baseline dan Intervensi KUR?"):
        st.write("Baseline mensimulasikan kondisi normal. Intervensi KUR menambahkan subsidi bunga, pendampingan, dan penguatan cashflow sehingga risiko lebih rendah.")

    with st.expander("Mengapa hasil berbeda setiap kali dijalankan?"):
        st.write("Simulasi bersifat stochastic. Gunakan random seed yang sama untuk mendapatkan hasil identik. Monte Carlo mengukur variasi hasil ini.")

    with st.expander("Apakah dataset ini asli?"):
        st.write("Tidak. Dataset bersifat sintetis, dibuat dengan aturan logis agar sesuai konteks kredit mikro UMKM Indonesia.")

    with st.expander("Bagaimana menggunakan skenario custom?"):
        st.write("Buka sidebar, aktifkan toggle Skenario Custom, lalu atur parameter. Skenario custom akan muncul di semua tab analisis.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Referensi**")
    st.markdown(
        """
        <div class="info-card">
            <div style="color:#A1A1AA; line-height:1.8; font-size:13px;">
                Wilensky, U. & Rand, W. (2015). <i>An Introduction to Agent-Based Modeling</i>. MIT Press.<br>
                Bank Indonesia — Laporan Perkembangan Kredit UMKM.<br>
                OJK — Statistik Perbankan Indonesia.<br>
                Streamlit Documentation — <a href="https://docs.streamlit.io" style="color:#3B82F6;" target="_blank">docs.streamlit.io</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# FOOTER
# =============================================================================
st.markdown(
    '<div class="footer-note">'
    'Final Project Pemodelan dan Simulasi Data C — Ahmad Hamdan Hamidiy'
    '</div>',
    unsafe_allow_html=True,
)
