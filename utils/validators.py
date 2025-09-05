from __future__ import annotations

from typing import Iterable, List, Mapping
import pandas as pd


def check_missing(df: pd.DataFrame, required: Iterable[str]) -> List[str]:
    required = list(required)
    return [c for c in required if c not in df.columns]


def check_positive(df: pd.DataFrame, cols: Iterable[str]) -> List[str]:
    bad: List[str] = []
    for c in cols:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        if (s < 0).any():
            bad.append(c)
    return bad


def validate_all(
    mats: pd.DataFrame,
    procs: pd.DataFrame,
    bom: pd.DataFrame,
) -> Mapping[str, Mapping[str, list]]:
    report = {
        "materials": {"missing": [], "negative": []},
        "processes": {"missing": [], "negative": []},
        "bom": {"missing": [], "negative": []},
    }

    report["materials"]["missing"] += check_missing(
        mats, ["material_id", "price_eur_per_kg"]
    )
    report["materials"]["negative"] += check_positive(
        mats, ["price_eur_per_kg"]
    )

    report["processes"]["missing"] += check_missing(
        procs,
        [
            "process_id",
            "machine_rate_eur_h",
            "labor_rate_eur_h",
            "overhead_pct",
            "margin_pct",
        ],
    )
    report["processes"]["negative"] += check_positive(
        procs,
        ["machine_rate_eur_h", "labor_rate_eur_h", "overhead_pct", "margin_pct"],
    )

    report["bom"]["missing"] += check_missing(
        bom, ["line_id", "material_id", "qty", "mass_kg", "process_route", "runtime_h"]
    )
    report["bom"]["negative"] += check_positive(
        bom, ["qty", "mass_kg", "runtime_h"]
    )

    return report
