from __future__ import annotations

import numpy as np
import pandas as pd

LOSS_GIVEN_DEFAULT = 0.55
DEFAULT_THRESHOLD = 0.45

SCENARIOS = {
    "Baseline": {
        "description": "Kondisi normal dengan seleksi kredit standar.",
        "approval_threshold": 50,
        "annual_interest_rate": 0.12,
        "base_stressor": 0.075,
        "stressor_std": 0.035,
        "intervention_strength": 0.08,
        "contagion_strength": 0.10,
        "default_sensitivity": 1.00,
    },
    "Guncangan Ekonomi": {
        "description": "Tekanan ekonomi meningkat sehingga omzet UMKM lebih rentan turun.",
        "approval_threshold": 50,
        "annual_interest_rate": 0.12,
        "base_stressor": 0.125,
        "stressor_std": 0.060,
        "intervention_strength": 0.06,
        "contagion_strength": 0.18,
        "default_sensitivity": 1.18,
    },
    "Intervensi KUR": {
        "description": "Ada subsidi bunga, pendampingan, dan penguatan cashflow untuk menekan risiko.",
        "approval_threshold": 50,
        "annual_interest_rate": 0.07,
        "base_stressor": 0.082,
        "stressor_std": 0.035,
        "intervention_strength": 0.18,
        "contagion_strength": 0.08,
        "default_sensitivity": 0.86,
    },
    "Seleksi Kredit Ketat": {
        "description": "Bank menaikkan ambang skor kredit sehingga hanya UMKM lebih sehat yang disetujui.",
        "approval_threshold": 62,
        "annual_interest_rate": 0.12,
        "base_stressor": 0.070,
        "stressor_std": 0.032,
        "intervention_strength": 0.10,
        "contagion_strength": 0.07,
        "default_sensitivity": 0.92,
    },
}


def build_custom_scenario(base_name: str, annual_interest_rate: float, base_stressor: float,
                          intervention_strength: float, approval_threshold: float) -> dict:
    """Membuat skenario custom dari salah satu skenario bawaan."""
    scenario = SCENARIOS[base_name].copy()
    scenario["description"] = "Skenario custom dari parameter sidebar."
    scenario["annual_interest_rate"] = annual_interest_rate
    scenario["base_stressor"] = base_stressor
    scenario["intervention_strength"] = intervention_strength
    scenario["approval_threshold"] = approval_threshold
    return scenario


def run_single_simulation(df: pd.DataFrame, scenario: dict, n_months: int = 24, seed: int = 42,
                          default_threshold: float = DEFAULT_THRESHOLD,
                          loss_given_default: float = LOSS_GIVEN_DEFAULT) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Menjalankan satu kali simulasi ABM.

    Agen yang disetujui kreditnya akan mengalami perubahan risiko setiap bulan.
    Risiko dipengaruhi stressor ekonomi, vulnerability, debt burden, contagion,
    resilience, dan kekuatan intervensi.
    """
    rng = np.random.default_rng(seed)
    agents = df.copy().reset_index(drop=True)
    approved = agents["credit_score"].to_numpy() >= scenario["approval_threshold"]

    n_approved = int(approved.sum())
    if n_approved == 0:
        empty = pd.DataFrame({
            "bulan": list(range(1, n_months + 1)),
            "approved_agents": 0,
            "new_defaults": 0,
            "cumulative_defaults": 0,
            "default_rate": 0.0,
            "avg_risk": 0.0,
            "monthly_profit": 0.0,
            "cumulative_profit": 0.0,
            "stressor": 0.0,
            "active_agents": 0,
        })
        agents["approved"] = approved
        agents["defaulted"] = False
        agents["final_risk"] = agents["initial_risk"]
        return empty, agents

    risk = agents["initial_risk"].to_numpy(dtype=float).copy()
    vulnerability = agents["vulnerability"].to_numpy(dtype=float)
    resilience = agents["resilience"].to_numpy(dtype=float)
    debt_burden = agents["debt_burden"].to_numpy(dtype=float)
    loan = agents["pinjaman"].to_numpy(dtype=float)

    defaulted = np.zeros(len(agents), dtype=bool)
    cumulative_profit = 0.0
    rows = []

    for month in range(1, n_months + 1):
        active = approved & (~defaulted)
        previous_default_rate = defaulted[approved].mean() if n_approved > 0 else 0.0

        # Stressor dibuat berfluktuasi per bulan agar simulasi lebih realistis.
        seasonal = 0.015 * np.sin(month / 3.0)
        stressor = float(np.clip(rng.normal(scenario["base_stressor"] + seasonal, scenario["stressor_std"]), 0, 0.35))
        contagion = previous_default_rate * scenario["contagion_strength"]

        updated_risk = (
            0.82 * risk
            + (stressor * vulnerability * scenario["default_sensitivity"])
            + (0.070 * debt_burden)
            + contagion
            - (resilience * scenario["intervention_strength"])
        )
        risk = np.clip(updated_risk, 0, 1)

        # Probabilitas default meningkat tajam jika risk melewati threshold.
        raw_probability = 1 / (1 + np.exp(-12 * (risk - default_threshold)))
        default_probability = np.clip(raw_probability * 0.075, 0.002, 0.42)
        random_draw = rng.random(len(agents))
        new_default = active & (random_draw < default_probability)
        defaulted = defaulted | new_default

        monthly_interest_income = loan[active].sum() * (scenario["annual_interest_rate"] / 12)
        monthly_loss = loan[new_default].sum() * loss_given_default
        monthly_profit = monthly_interest_income - monthly_loss
        cumulative_profit += monthly_profit

        rows.append({
            "bulan": month,
            "approved_agents": n_approved,
            "new_defaults": int(new_default.sum()),
            "cumulative_defaults": int(defaulted[approved].sum()),
            "default_rate": float(defaulted[approved].mean()),
            "avg_risk": float(risk[approved].mean()),
            "monthly_profit": float(monthly_profit),
            "cumulative_profit": float(cumulative_profit),
            "stressor": stressor,
            "active_agents": int(active.sum()),
        })

    agents["approved"] = approved
    agents["defaulted"] = defaulted
    agents["final_risk"] = np.round(risk, 4)
    return pd.DataFrame(rows), agents


def run_scenarios(df: pd.DataFrame, scenario_names: list[str], n_months: int = 24, seed: int = 42) -> dict:
    """Menjalankan simulasi untuk beberapa skenario bawaan."""
    results = {}
    for idx, name in enumerate(scenario_names):
        monthly, agents = run_single_simulation(df, SCENARIOS[name], n_months=n_months, seed=seed + idx * 101)
        results[name] = {"monthly": monthly, "agents": agents, "scenario": SCENARIOS[name]}
    return results


def summarize_results(results: dict) -> pd.DataFrame:
    """Membuat tabel ringkasan dari hasil beberapa skenario."""
    rows = []
    for name, result in results.items():
        monthly = result["monthly"]
        agents = result["agents"]
        scenario = result["scenario"]
        last = monthly.iloc[-1]
        rows.append({
            "Skenario": name,
            "Deskripsi": scenario["description"],
            "Approval Rate": agents["approved"].mean(),
            "Jumlah Agen Approved": int(agents["approved"].sum()),
            "Default Rate Akhir": last["default_rate"],
            "Rata-rata Risiko Akhir": last["avg_risk"],
            "Profit Kumulatif": last["cumulative_profit"],
            "Total Default": int(last["cumulative_defaults"]),
        })
    return pd.DataFrame(rows)


def run_monte_carlo(df: pd.DataFrame, scenario_name: str, n_runs: int = 1000, n_months: int = 24,
                    seed: int = 42) -> pd.DataFrame:
    """Menjalankan Monte Carlo untuk satu skenario."""
    scenario = SCENARIOS[scenario_name]
    rows = []
    for i in range(n_runs):
        monthly, agents = run_single_simulation(df, scenario, n_months=n_months, seed=seed + i)
        last = monthly.iloc[-1]
        rows.append({
            "run": i + 1,
            "skenario": scenario_name,
            "approval_rate": agents["approved"].mean(),
            "default_rate_akhir": last["default_rate"],
            "avg_risk_akhir": last["avg_risk"],
            "profit_kumulatif": last["cumulative_profit"],
            "total_default": int(last["cumulative_defaults"]),
        })
    return pd.DataFrame(rows)


def compute_convergence(mc_df: pd.DataFrame) -> pd.DataFrame:
    """Menghitung rata-rata kumulatif default rate seiring bertambahnya iterasi MC.

    Berguna untuk menunjukkan bahwa hasil Monte Carlo konvergen.
    """
    cumulative_mean = mc_df["default_rate_akhir"].expanding().mean()
    cumulative_std = mc_df["default_rate_akhir"].expanding().std().fillna(0)
    return pd.DataFrame({
        "iterasi": mc_df["run"],
        "cumulative_mean": cumulative_mean,
        "cumulative_std": cumulative_std,
        "upper_band": cumulative_mean + cumulative_std,
        "lower_band": (cumulative_mean - cumulative_std).clip(lower=0),
    })


def agent_status_over_time(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """Menghitung jumlah agen aktif vs default per bulan untuk stacked area chart."""
    result = monthly_df[["bulan", "approved_agents", "cumulative_defaults", "active_agents"]].copy()
    result["defaulted_agents"] = result["cumulative_defaults"]
    return result


def sensitivity_intervention(df: pd.DataFrame, base_scenario_name: str = "Intervensi KUR", values=None,
                             n_runs_per_value: int = 100, n_months: int = 24, seed: int = 42) -> pd.DataFrame:
    """Menguji pengaruh kekuatan intervensi terhadap default rate akhir."""
    if values is None:
        values = np.round(np.linspace(0.04, 0.24, 8), 3)

    base = SCENARIOS[base_scenario_name].copy()
    rows = []
    for j, value in enumerate(values):
        scenario = base.copy()
        scenario["intervention_strength"] = float(value)
        defaults = []
        profits = []
        for i in range(n_runs_per_value):
            monthly, _ = run_single_simulation(df, scenario, n_months=n_months, seed=seed + j * 1000 + i)
            defaults.append(float(monthly.iloc[-1]["default_rate"]))
            profits.append(float(monthly.iloc[-1]["cumulative_profit"]))
        rows.append({
            "intervention_strength": float(value),
            "mean_default_rate": float(np.mean(defaults)),
            "std_default_rate": float(np.std(defaults)),
            "mean_profit": float(np.mean(profits)),
        })
    return pd.DataFrame(rows)


def format_rupiah(value: float) -> str:
    """Format angka ke Rupiah singkat."""
    value = float(value)
    if abs(value) >= 1_000_000_000:
        return f"Rp {value/1_000_000_000:,.2f} M".replace(",", ".")
    if abs(value) >= 1_000_000:
        return f"Rp {value/1_000_000:,.2f} Jt".replace(",", ".")
    return f"Rp {value:,.0f}".replace(",", ".")
