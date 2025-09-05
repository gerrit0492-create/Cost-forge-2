from pathlib import Path
import pandas as pd
SCHEMA_MATERIALS={"material_id":"string","description":"string","price_eur_per_kg":"float64"}
SCHEMA_PROCESSES={"process_id":"string","machine_rate_eur_h":"float64","labor_rate_eur_h":"float64","overhead_pct":"float64","margin_pct":"float64"}
SCHEMA_BOM={"line_id":"string","material_id":"string","qty":"Int64","mass_kg":"float64","process_route":"string","runtime_h":"float64"}
SCHEMA_QUOTES={"supplier":"string","material_id":"string","price_eur_per_kg":"float64","lead_time_days":"Int64","valid_until":"string","preferred":"Int64"}
def paths():
    d=Path("data")
    return {"materials":d/"materials_db.csv","processes":d/"processes_db.csv","bom":d/"bom_template.csv","quotes":d/"supplier_quotes.csv"}
def _read_csv(p, schema=None):
    if schema is None: return pd.read_csv(p)
    dtypes={k:v for k,v in schema.items() if v!="Int64"}
    df=pd.read_csv(p,dtype=dtypes)
    for c,t in schema.items():
        if t=="Int64" and c in df.columns: df[c]=df[c].astype("Int64")
    return df
def load_materials(): return _read_csv(paths()["materials"],SCHEMA_MATERIALS)
def load_processes(): return _read_csv(paths()["processes"],SCHEMA_PROCESSES)
def load_bom(): return _read_csv(paths()["bom"],SCHEMA_BOM)
def load_quotes(): return _read_csv(paths()["quotes"],SCHEMA_QUOTES)
