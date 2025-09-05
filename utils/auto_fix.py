from pathlib import Path

import pandas as pd


def normalize_headers_csv(path: Path, rename_map: dict[str, str]) -> bool:
    if not path.exists():
        return False
    df = pd.read_csv(path)
    df = df.rename(columns=rename_map)
    df.to_csv(path, index=False)
    return True
