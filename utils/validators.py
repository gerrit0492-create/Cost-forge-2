from __future__ import annotations
import pandas as pd

def check_positive(df: pd.DataFrame, cols: list[str]) -> list[str]:
    issues = []
    for c in cols:
        if c in df.columns and (df[c] < 0).any():
            issues.append(f"Kolom '{c}' bevat negatieve waarden")
    return issues

def check_missing(df: pd.DataFrame, cols: list[str]) -> list[str]:
    return [f"Ontbrekende kolom: {c}" for c in cols if c not in df.columns]

def data_quality_report(mats: pd.DataFrame, procs: pd.DataFrame, bom: pd.DataFrame) -> dict:
    report = {"materials": [], "processes": [], "bom": []}
    report["materials"] += check_missing(mats, ["material_id","price_eur_per_kg"])
    report["materials"] += check_positive(mats, ["price_eur_per_kg"])
    report["processes"] += check_missing(procs, ["process_id","machine_rate_eur_h","labor_rate_eur_h","overhead_pct","margin_pct"])
    report["processes"] += check_positive(procs, ["machine_rate_eur_h","labor_rate_eur_h","overhead_pct","margin_pct"])
    report["bom"] += check_missing(bom, ["line_id","material_id","qty","mass_kg","process_route","runtime_h"])
    report["bom"] += check_positive(bom, ["qty","mass_kg","runtime_h"])
    return report
