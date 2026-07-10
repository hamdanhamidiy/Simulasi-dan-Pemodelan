from pathlib import Path
import numpy as np
import pandas as pd


def make_umkm_dataset(n_agents: int = 500, seed: int = 42) -> pd.DataFrame:
    """Membuat dataset dummy UMKM yang logis untuk simulasi ABM.

    Dataset dibuat dummy karena fokus tugas adalah simulasi. Nilai yang dibuat tetap
    mengikuti logika kredit mikro: usaha dengan cashflow, margin, literasi keuangan,
    agunan, dan digitalisasi lebih baik akan cenderung memiliki skor kredit lebih tinggi.
    """
    rng = np.random.default_rng(seed)

    sectors = np.array(["Kuliner", "Retail", "Jasa", "Produksi", "Pertanian"])
    sector_prob = np.array([0.30, 0.25, 0.18, 0.15, 0.12])
    sektor = rng.choice(sectors, size=n_agents, p=sector_prob)

    usia_usaha_tahun = rng.integers(1, 13, size=n_agents)
    omzet_bulanan = rng.lognormal(mean=np.log(18_000_000), sigma=0.55, size=n_agents)
    omzet_bulanan = np.clip(omzet_bulanan, 3_000_000, 120_000_000)

    margin_laba = rng.normal(0.22, 0.07, size=n_agents)
    margin_laba = np.clip(margin_laba, 0.05, 0.45)

    cashflow_ratio = rng.normal(0.62, 0.17, size=n_agents)
    cashflow_ratio = np.clip(cashflow_ratio, 0.12, 1.00)

    pinjaman = rng.lognormal(mean=np.log(35_000_000), sigma=0.50, size=n_agents)
    pinjaman = np.clip(pinjaman, 5_000_000, 200_000_000)

    tenor_bulan = rng.choice([12, 18, 24, 36], size=n_agents, p=[0.25, 0.25, 0.35, 0.15])
    agunan = rng.choice([0, 1], size=n_agents, p=[0.58, 0.42])
    literasi_keuangan = rng.uniform(0.25, 0.95, size=n_agents)
    digitalisasi = rng.uniform(0.10, 0.90, size=n_agents)

    # Faktor sektor menunjukkan tingkat kerentanan sektor terhadap tekanan ekonomi.
    sector_risk_map = {
        "Kuliner": 0.62,
        "Retail": 0.58,
        "Jasa": 0.52,
        "Produksi": 0.56,
        "Pertanian": 0.68,
    }
    sector_risk = np.array([sector_risk_map[s] for s in sektor])

    debt_burden = pinjaman / (omzet_bulanan * np.maximum(tenor_bulan, 1))
    debt_burden_norm = np.clip(debt_burden * 6, 0, 1)

    credit_score = (
        38
        + usia_usaha_tahun * 1.35
        + cashflow_ratio * 24
        + margin_laba * 18
        + literasi_keuangan * 14
        + digitalisasi * 8
        + agunan * 7
        - debt_burden_norm * 18
        - sector_risk * 7
        + rng.normal(0, 4, size=n_agents)
    )
    credit_score = np.clip(credit_score, 0, 100)

    initial_risk = (
        0.62
        - credit_score / 180
        + debt_burden_norm * 0.22
        + sector_risk * 0.16
        - agunan * 0.05
        + rng.normal(0, 0.035, size=n_agents)
    )
    initial_risk = np.clip(initial_risk, 0.04, 0.92)

    vulnerability = np.clip(0.30 + sector_risk * 0.52 + debt_burden_norm * 0.26 - cashflow_ratio * 0.18, 0.08, 0.95)
    resilience = np.clip(0.18 + cashflow_ratio * 0.34 + literasi_keuangan * 0.28 + digitalisasi * 0.18 + agunan * 0.08, 0.06, 0.92)

    df = pd.DataFrame({
        "id_umkm": np.arange(1, n_agents + 1),
        "sektor": sektor,
        "usia_usaha_tahun": usia_usaha_tahun,
        "omzet_bulanan": omzet_bulanan.round(0).astype(int),
        "margin_laba": np.round(margin_laba, 3),
        "cashflow_ratio": np.round(cashflow_ratio, 3),
        "pinjaman": pinjaman.round(0).astype(int),
        "tenor_bulan": tenor_bulan,
        "agunan": agunan,
        "literasi_keuangan": np.round(literasi_keuangan, 3),
        "digitalisasi": np.round(digitalisasi, 3),
        "debt_burden": np.round(debt_burden_norm, 3),
        "credit_score": np.round(credit_score, 2),
        "initial_risk": np.round(initial_risk, 3),
        "vulnerability": np.round(vulnerability, 3),
        "resilience": np.round(resilience, 3),
    })
    return df


def load_or_create_dataset(path: str | Path = "data/dataset_umkm_dummy.csv", n_agents: int = 500, seed: int = 42) -> pd.DataFrame:
    """Memuat dataset jika sudah ada, atau membuat dataset baru jika file belum tersedia."""
    path = Path(path)
    if path.exists():
        return pd.read_csv(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    df = make_umkm_dataset(n_agents=n_agents, seed=seed)
    df.to_csv(path, index=False)
    return df
