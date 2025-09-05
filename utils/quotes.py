import pandas as pd


def best_quotes(quotes: pd.DataFrame) -> pd.DataFrame:
    q = quotes.copy()
    q["preferred"] = q.get("preferred", 0)
    q["lead_time_days"] = q.get("lead_time_days", 999_999)
    q = q.sort_values(
        by=["material_id", "preferred", "price_eur_per_kg", "lead_time_days"],
        ascending=[True, False, True, True],
    )
    return q.groupby("material_id").head(1).reset_index(drop=True)


def apply_best_quotes(materials: pd.DataFrame, quotes: pd.DataFrame) -> pd.DataFrame:
    best = best_quotes(quotes)
    m = materials.merge(
        best[["material_id", "price_eur_per_kg", "supplier", "lead_time_days"]],
        on="material_id",
        how="left",
        suffixes=("", "_quote"),
    )
    if "price_eur_per_kg_quote" in m.columns:
        if "price_eur_per_kg" not in m.columns:
            m["price_eur_per_kg"] = m["price_eur_per_kg_quote"]
        else:
            m["price_eur_per_kg"] = m["price_eur_per_kg"].fillna(m["price_eur_per_kg_quote"])
        m = m.drop(columns=["price_eur_per_kg_quote"])
    return m


def join_with_materials(materials: pd.DataFrame, best: pd.DataFrame) -> pd.DataFrame:
    return materials.drop(columns=["price_eur_per_kg"], errors="ignore").merge(
        best[["material_id", "supplier", "price_eur_per_kg", "lead_time_days"]],
        on="material_id",
        how="left",
    )
