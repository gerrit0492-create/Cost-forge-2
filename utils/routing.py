import pandas as pd
def compute_routing_cost(bom: pd.DataFrame, routing: pd.DataFrame) -> pd.DataFrame:
    df = bom.merge(routing, how="left", left_on="process_route", right_on="process_id")
    df["routing_time_h"] = (df.get("time_h_per_unit",0)*df["qty"]).fillna(0) + df.get("setup_h",0).fillna(0)
    return df
def routing_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "routing_time_h" not in df.columns:
        return pd.DataFrame(columns=["process_id","routing_time_h"])
    return df.groupby("process_id", dropna=False)["routing_time_h"].sum().reset_index()
