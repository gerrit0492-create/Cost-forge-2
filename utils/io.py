from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

SCHEMA_MATERIALS: Dict[str, Any] = {
    "material_id": "string",
    "description": "string",
    "price_eur_per_kg": "float64",
}
SCHEMA_PROCESSES: Dict[str, Any] = {
    "process_id": "string",
    "machine_rate_eur_h": "float64",
    "labor_rate_eur_h": "float64",
    "overhead_pct": "float64",
    "margin_pct": "float64",
}
SCHEMA_BOM: Dict[str, Any] = {
    "line_id": "string",
    "material_id": "string",
    "qty": "Int64",
    "mass_kg": "float64",
    "process_route": "string",
    "runtime_h": "float64",
}
SCHEMA_QUOTES: Dict[str, Any] = {
    "supplier": "string",
    "material_id": "string",
    "price_eur_per_kg": "float64",
    "lead_time_days": "Int64",
    "valid_until": "string",
    "preferred": "Int64",
}

def paths() -> Dict[str, Path]:
    d = Path("data")
    return {
        "root": Path("."),
        "data": d,
        "materials": d / "materials_db.csv",
        "processes": d / "processes_db.csv",
        "bom": d / "bom_template.csv",
        "quotes": d / "supplier_quotes.csv",
    }

def _dtype_map(schema: Dict[str, Any]) -> Dict[str, Any]:
    return dict(schema)

def _read_csv(path: Path, schema: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    if schema is None:
        return pd.read_csv(path)
    dtypes = _dtype_map(schema)
    df = pd.read_csv(path, dtype={k: v for k, v in dtypes.items() if v != "Int64"})
    for col, typ in dtypes.items():
        if typ == "Int64" and col in df.columns:
            df[col] = df[col].astype("Int64")
    return df

def load_materials() -> pd.DataFrame:
    return _read_csv(paths()["materials"], SCHEMA_MATERIALS)

def load_processes() -> pd.DataFrame:
    return _read_csv(paths()["processes"], SCHEMA_PROCESSES)

def load_bom() -> pd.DataFrame:
    return _read_csv(paths()["bom"], SCHEMA_BOM)

def load_quotes() -> pd.DataFrame:
    return _read_csv(paths()["quotes"], SCHEMA_QUOTES)
