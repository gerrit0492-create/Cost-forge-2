from __future__ import annotations
import pandas as pd

def best_quotes(quotes: pd.DataFrame) -> pd.DataFrame:
    q = quotes.copy()
    if "preferred" in q.columns:
        q["preferred"] = q["preferred"].fillna(0)
    else:
        q["preferred"] = 0
    q["lead_time_days"] = q["lead_time_days"].fillna(999999)
    q = q.sort_values(by=["material_id","preferred","price_eur_per_kg","lead_time_days"],
                      ascending=[True, False, True, True])
    idx = q.groupby("material_id").head(1).index
    return q.loc[idx].reset_index(drop=True)

def apply_best_quotes(materials: pd.DataFrame, quotes: pd.DataFrame) -> pd.DataFrame:
    best = best_quotes(quotes)
    m = materials.copy()
    m = m.drop(columns=["price_eur_per_kg"], errors="ignore")          .merge(best[["material_id","price_eur_per_kg","supplier","lead_time_days"]], on="material_id", how="left")
    m = m.rename(columns={"price_eur_per_kg":"price_eur_per_kg_from_quote"})
    if "price_eur_per_kg_from_quote" in m.columns:
        if "price_eur_per_kg" not in m.columns:
            m["price_eur_per_kg"] = m["price_eur_per_kg_from_quote"]
        else:
            m["price_eur_per_kg"] = m["price_eur_per_kg"].fillna(m["price_eur_per_kg_from_quote"])
    return m

def join_with_materials(materials: pd.DataFrame, best: pd.DataFrame) -> pd.DataFrame:
    return materials.drop(columns=["price_eur_per_kg"], errors="ignore")         .merge(best[["material_id","supplier","price_eur_per_kg","lead_time_days"]],
               on="material_id", how="left")
