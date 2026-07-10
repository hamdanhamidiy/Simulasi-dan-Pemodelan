import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_generator import load_or_create_dataset, make_umkm_dataset
from src.simulation import (
    SCENARIOS,
    build_custom_scenario,
    format_rupiah,
    run_monte_carlo,
    run_scenarios,
    run_single_simulation,
    sensitivity_intervention,
    summarize_results,
)
from src.styles import inject_custom_css

st.set_page_config(
    page_title="Dashboard ABM Kredit Mikro UMKM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.markdown("# 📊 ABM UMKM")
st.sidebar.caption("Dashboard simulasi risiko kredit mikro UMKM")

with st.sidebar.expander("⚙️ Pengaturan Simulasi", expanded=True):
    n_agents = st.slider("Jumlah agen UMKM", 100, 1000, 500, step=50)
    n_months = st.slider("Durasi simulasi (bulan)", 12, 60, 24, step=6)
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42, step=1)
    n_monte_carlo = st.slider("Iterasi Monte Carlo", 50, 1000, 300, step=50)

with st.sidebar.expander("🎯 Pilih Skenario", expanded=True):
    scenario_names = st.multiselect(
        "Skenario yang dibandingkan",
        options=list(SCENARIOS.keys()),
        default=list(SCENARIOS.keys()),
    )
    mc_scenario = st.selectbox("Skenario untuk Monte Carlo", options=list(SCENARIOS.keys()), index=2)

with st.sidebar.expander("🧪 Skenario Custom", expanded=False):
    use_custom = st.toggle("Aktifkan skenario custom", value=False)
    custom_base = st.selectbox("Basis skenario", list(SCENARIOS.keys()), index=0)
    custom_interest = st.slider("Bunga tahunan custom", 0.03, 0.24, 0.10, step=0.01)
    custom_stressor = st.slider("Stressor ekonomi custom", 0.02, 0.22, 0.08, step=0.01)
    custom_intervention = st.slider("Kekuatan intervensi custom", 0.00, 0.30, 0.12, step=0.01)
    custom_threshold = st.slider("Ambang approval custom", 30, 85, 55, step=1)

run_button = st.sidebar.button("🚀 Jalankan / Refresh Simulasi", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "Untuk memenuhi tugas, gunakan Monte Carlo 1000 iterasi saat hasil akhir. "
    "Saat mencoba tampilan, 200–300 iterasi sudah cukup agar dashboard lebih cepat."
)

# -----------------------------------------------------------------------------
# CACHE FUNCTIONS
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# DATA & SIMULATION
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Dashboard Simulasi ABM Risiko Kredit Mikro UMKM</div>
        <div class="hero-subtitle">
            Simulasi berbasis agen untuk menganalisis risiko gagal bayar kredit mikro UMKM
            melalui skenario <i>what-if</i>, Monte Carlo, dan analisis sensitivitas intervensi.
            <br><b>Ahmad Hamdan Hamidiy</b> — hamdanhamidiy2687@webmail.ac.id
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# GLOBAL METRICS
# -----------------------------------------------------------------------------
best_row = summary_df.sort_values("Default Rate Akhir", ascending=True).iloc[0]
worst_row = summary_df.sort_values("Default Rate Akhir", ascending=False).iloc[0]
profit_best = summary_df.sort_values("Profit Kumulatif", ascending=False).iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Jumlah Agen", f"{len(df):,}".replace(",", "."))
m2.metric("Skenario Terendah Default", best_row["Skenario"], f"{best_row['Default Rate Akhir']*100:.2f}%")
m3.metric("Skenario Tertinggi Default", worst_row["Skenario"], f"{worst_row['Default Rate Akhir']*100:.2f}%")
m4.metric("Profit Kumulatif Tertinggi", profit_best["Skenario"], format_rupiah(profit_best["Profit Kumulatif"]))

# -----------------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Ringkasan",
    "🏪 Dataset UMKM",
    "📈 Simulasi What-If",
    "🎲 Monte Carlo",
    "🧠 Formulasi Model",
])

with tab1:
    st.markdown('<div class="section-title">Ringkasan Perbandingan Skenario</div>', unsafe_allow_html=True)
    st.write(
        "Bagian ini memperlihatkan perbandingan utama antar skenario. "
        "Indikator yang paling penting adalah default rate akhir, approval rate, rata-rata risiko, dan profit kumulatif."
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
            summary_df,
            x="Skenario",
            y="Default Rate Akhir",
            text=summary_df["Default Rate Akhir"].map(lambda x: f"{x*100:.2f}%"),
            title="Default Rate Akhir per Skenario",
        )
        fig.update_layout(yaxis_tickformat=".0%", height=420)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            summary_df,
            x="Skenario",
            y="Profit Kumulatif",
            title="Estimasi Profit Kumulatif per Skenario",
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown("**Interpretasi cepat:**")
    st.write(
        f"Skenario dengan default rate paling rendah adalah **{best_row['Skenario']}**. "
        f"Skenario dengan default rate paling tinggi adalah **{worst_row['Skenario']}**. "
        "Jika hasil ini digunakan untuk jurnal, pembahasan dapat diarahkan pada efektivitas intervensi, "
        "dampak stressor ekonomi, dan trade-off antara seleksi kredit dengan jangkauan pembiayaan UMKM."
    )
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-title">Dataset Dummy UMKM</div>', unsafe_allow_html=True)
    st.write(
        "Dataset berisi agen UMKM. Setiap baris mewakili satu UMKM dengan atribut ekonomi dan kredit. "
        "Dataset ini dummy, tetapi dibangun menggunakan aturan logis agar sesuai dengan konteks kredit mikro."
    )

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Jumlah UMKM", len(df))
    col_b.metric("Rata-rata Skor Kredit", f"{df['credit_score'].mean():.2f}")
    col_c.metric("Rata-rata Risiko Awal", f"{df['initial_risk'].mean():.3f}")
    col_d.metric("Rata-rata Pinjaman", format_rupiah(df["pinjaman"].mean()))

    selected_sector = st.multiselect("Filter sektor", sorted(df["sektor"].unique()), default=sorted(df["sektor"].unique()))
    filtered_df = df[df["sektor"].isin(selected_sector)]

    st.dataframe(filtered_df.head(20), use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        sector_counts = filtered_df["sektor"].value_counts().reset_index()
        sector_counts.columns = ["sektor", "jumlah"]
        fig = px.pie(sector_counts, names="sektor", values="jumlah", title="Komposisi Agen per Sektor", hole=0.45)
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.histogram(filtered_df, x="credit_score", nbins=25, title="Distribusi Skor Kredit")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.box(filtered_df, x="sektor", y="initial_risk", title="Risiko Awal Berdasarkan Sektor")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.scatter(
            filtered_df,
            x="credit_score",
            y="initial_risk",
            size="pinjaman",
            color="sektor",
            hover_data=["omzet_bulanan", "cashflow_ratio", "debt_burden"],
            title="Hubungan Skor Kredit dan Risiko Awal",
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('<div class="section-title">Simulasi What-If per Bulan</div>', unsafe_allow_html=True)
    st.write(
        "Grafik di bawah menunjukkan perubahan default rate, rata-rata risiko, stressor, dan profit portofolio selama periode simulasi."
    )

    all_monthly = []
    for name, result in results.items():
        temp = result["monthly"].copy()
        temp["Skenario"] = name
        all_monthly.append(temp)
    all_monthly_df = pd.concat(all_monthly, ignore_index=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(
            all_monthly_df,
            x="bulan",
            y="default_rate",
            color="Skenario",
            markers=True,
            title="Perkembangan Default Rate Kumulatif",
        )
        fig.update_layout(yaxis_tickformat=".0%", height=430)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(
            all_monthly_df,
            x="bulan",
            y="avg_risk",
            color="Skenario",
            markers=True,
            title="Perkembangan Rata-rata Risiko Agen Approved",
        )
        fig.update_layout(height=430)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.line(
            all_monthly_df,
            x="bulan",
            y="cumulative_profit",
            color="Skenario",
            title="Profit Kumulatif Portofolio Kredit",
        )
        fig.update_layout(height=430)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.line(
            all_monthly_df,
            x="bulan",
            y="stressor",
            color="Skenario",
            title="Dinamika Stressor Ekonomi per Bulan",
        )
        fig.update_layout(height=430)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Detail Skenario")
    for name, result in results.items():
        st.markdown(
            f"<span class='scenario-pill'>{name}</span> "
            f"<span class='small-muted'>{result['scenario']['description']}</span>",
            unsafe_allow_html=True,
        )

with tab4:
    st.markdown('<div class="section-title">Monte Carlo dan Analisis Sensitivitas</div>', unsafe_allow_html=True)
    st.write(
        "Monte Carlo digunakan untuk melihat kestabilan hasil karena simulasi mengandung unsur acak. "
        "Untuk hasil akhir tugas, gunakan 1000 iterasi."
    )

    mc_df = cached_monte_carlo(df, mc_scenario, n_monte_carlo, n_months, seed)
    mean_default = mc_df["default_rate_akhir"].mean()
    ci_low = mc_df["default_rate_akhir"].quantile(0.025)
    ci_high = mc_df["default_rate_akhir"].quantile(0.975)

    cm1, cm2, cm3, cm4 = st.columns(4)
    cm1.metric("Skenario MC", mc_scenario)
    cm2.metric("Rata-rata Default", f"{mean_default*100:.2f}%")
    cm3.metric("CI 95% Default", f"{ci_low*100:.2f}% - {ci_high*100:.2f}%")
    cm4.metric("Rata-rata Profit", format_rupiah(mc_df["profit_kumulatif"].mean()))

    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(
            mc_df,
            x="default_rate_akhir",
            nbins=30,
            title=f"Distribusi Default Rate Akhir — {mc_scenario}",
        )
        fig.add_vline(x=mean_default, line_dash="dash", annotation_text="Mean")
        fig.update_layout(xaxis_tickformat=".0%", height=430)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(
            mc_df,
            x="default_rate_akhir",
            y="profit_kumulatif",
            trendline=None,
            title="Hubungan Default Rate dan Profit Kumulatif",
        )
        fig.update_layout(xaxis_tickformat=".0%", height=430)
        st.plotly_chart(fig, use_container_width=True)

    sens_df = cached_sensitivity(df, "Intervensi KUR", n_months, seed)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sens_df["intervention_strength"],
        y=sens_df["mean_default_rate"],
        mode="lines+markers",
        name="Mean Default Rate",
    ))
    fig.add_trace(go.Scatter(
        x=sens_df["intervention_strength"],
        y=sens_df["mean_default_rate"] + sens_df["std_default_rate"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=sens_df["intervention_strength"],
        y=sens_df["mean_default_rate"] - sens_df["std_default_rate"],
        mode="lines",
        fill="tonexty",
        line=dict(width=0),
        name="± Std",
        hoverinfo="skip",
    ))
    fig.update_layout(
        title="Sensitivitas Kekuatan Intervensi terhadap Default Rate",
        xaxis_title="Intervention Strength",
        yaxis_title="Mean Default Rate",
        yaxis_tickformat=".0%",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Lihat data hasil Monte Carlo"):
        st.dataframe(mc_df, use_container_width=True, hide_index=True)

with tab5:
    st.markdown('<div class="section-title">Formulasi Model ABM</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="soft-card">
        <b>Agen</b> pada simulasi ini adalah UMKM peminjam kredit mikro. Setiap agen memiliki atribut internal seperti skor kredit,
        cashflow, agunan, debt burden, vulnerability, resilience, dan risiko awal. Lingkungan memberikan tekanan berupa stressor ekonomi.
        Intervensi merepresentasikan kebijakan seperti KUR, subsidi bunga, pendampingan, atau seleksi kredit.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.latex(r"Risk_{t+1}=clip(0.82Risk_t + (S_t \times V \times \alpha) + B + C - (R \times P), 0, 1)")

    st.markdown(
        """
        Keterangan:

        - **Risk**: risiko gagal bayar agen UMKM.
        - **S**: stressor ekonomi pada bulan tertentu.
        - **V**: vulnerability atau kerentanan agen.
        - **α**: sensitivitas default pada skenario.
        - **B**: debt burden atau beban pinjaman.
        - **C**: contagion effect dari default rate sebelumnya.
        - **R**: resilience agen.
        - **P**: intervention strength atau kekuatan intervensi.
        - **clip(0,1)**: pembatas agar risiko tetap berada pada rentang 0 sampai 1.
        """
    )

    st.markdown("### Peta Kesesuaian dengan Ketentuan Tugas")
    compliance = pd.DataFrame({
        "Komponen Tugas": [
            "Pendekatan simulasi",
            "Agen",
            "Lingkungan",
            "Intervensi",
            "Variabel numerik",
            "Aturan transisi",
            "Skenario what-if",
            "Monte Carlo",
            "Dashboard",
        ],
        "Implementasi di Dashboard": [
            "Agent-Based Modeling berbasis Python",
            "UMKM peminjam kredit mikro",
            "Stressor ekonomi, sektor, dan contagion risk",
            "KUR, pendampingan, subsidi bunga, dan seleksi kredit",
            "Risk, credit score, debt burden, vulnerability, resilience",
            "Persamaan Risk(t+1) yang diperbarui per bulan",
            "Baseline, Guncangan Ekonomi, Intervensi KUR, Seleksi Kredit Ketat, Custom",
            "Dapat dijalankan hingga 1000 iterasi",
            "Streamlit dengan grafik interaktif dan tabel hasil",
        ],
    })
    st.dataframe(compliance, use_container_width=True, hide_index=True)

st.markdown(
    "<div class='footer-note'>Final Project Pemodelan dan Simulasi Data C — Ahmad Hamdan Hamidiy</div>",
    unsafe_allow_html=True,
)
