from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Sequence

import pandas as pd


def check_missing(df: pd.DataFrame, required: Iterable[str]) -> List[str]:
    req = list(required)
    return [c for c in req if c not in df.columns]


def check_positive(df: pd.DataFrame, cols: Iterable[str]) -> List[str]:
    bad = []
    for c in cols:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        if (s <= 0).any():
            bad.append(c)
    return bad


def validate_all(
    mats: pd.DataFrame, procs: pd.DataFrame, bom: pd.DataFrame
) -> Mapping[str, Mapping[str, list]]:
    rpt = {
        "materials": {"missing": [], "nonpositive": []},
        "processes": {"missing": [], "nonpositive": []},
        "bom": {"missing": [], "nonpositive": []},
    }
    rpt["materials"]["missing"] += check_missing(mats, ["material_id", "price_eur_per_kg"])
    rpt["materials"]["nonpositive"] += check_positive(mats, ["price_eur_per_kg"])

    rpt["processes"]["missing"] += check_missing(
        procs,
        ["process_id", "machine_rate_eur_h", "labor_rate_eur_h", "overhead_pct", "margin_pct"],
    )
    # machine/labor > 0; overhead/margin >= 0 (mag 0 zijn)
    rpt["processes"]["nonpositive"] += check_positive(
        procs, ["machine_rate_eur_h", "labor_rate_eur_h"]
    )
    return rpt


# ---------- Cost-engineering guardrails ----------

@dataclass(frozen=True)
class Rule:
    name: str
    ok: bool
    msg: str


def within(df: pd.DataFrame, col: str, lo: float | None, hi: float | None) -> bool:
    if col not in df.columns:
        return False
    s = pd.to_numeric(df[col], errors="coerce")
    good = True
    if lo is not None:
        good &= (s >= lo).all()
    if hi is not None:
        good &= (s <= hi).all()
    return bool(good)


def business_rules(mats: pd.DataFrame, procs: pd.DataFrame, bom: pd.DataFrame) -> List[Rule]:
    rules: List[Rule] = []

    # 1) Tarieven > 0
    rules.append(
        Rule(
            "rates_positive",
            within(procs, "machine_rate_eur_h", 0.01, None)
            and within(procs, "labor_rate_eur_h", 0.01, None),
            "Machine- en arbeidsloon moeten > 0 zijn.",
        )
    )

    # 2) Overhead/marge in [0, 1]
    rules.append(
        Rule(
            "overhead_pct_range",
            within(procs, "overhead_pct", 0.0, 1.0),
            "overhead_pct moet tussen 0 en 1 liggen.",
        )
    )
    rules.append(
        Rule(
            "margin_pct_range",
            within(procs, "margin_pct", 0.0, 1.0),
            "margin_pct moet tussen 0 en 1 liggen.",
        )
    )

    # 3) BOM: qty >= 1, mass_kg > 0, runtime_h >= 0
    rules.append(
        Rule("qty_min_1", within(bom, "qty", 1, None), "qty moet >= 1 zijn.")
    )
    rules.append(
        Rule("mass_positive", within(bom, "mass_kg", 0.000001, None), "mass_kg moet > 0 zijn.")
    )
    rules.append(
        Rule("runtime_nonneg", within(bom, "runtime_h", 0.0, None), "runtime_h moet >= 0 zijn.")
    )

    # 4) Materialen: prijs > 0
    rules.append(
        Rule(
            "mat_price_pos",
            within(mats, "price_eur_per_kg", 0.000001, None),
            "Materiaalprijs moet > 0 zijn.",
        )
    )

    return rules


def summarize_rules(rules: Sequence[Rule]) -> str:
    lines = []
    for r in rules:
        prefix = "✅" if r.ok else "❌"
        lines.append(f"{prefix} {r.name}: {r.msg if not r.ok else 'OK'}")
    return "\n".join(lines)


def all_rules_ok(rules: Sequence[Rule]) -> bool:
    return all(r.ok for r in rules)
