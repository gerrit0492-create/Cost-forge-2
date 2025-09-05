import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict
PRESETS_FILE = Path("data/presets.json")
@dataclass
class PricingPreset:
    name: str
    overhead_pct: float
    margin_pct: float
DEFAULTS: Dict[str, PricingPreset] = {
    "Standard": PricingPreset("Standard", 0.20, 0.10),
    "Aggressive": PricingPreset("Aggressive", 0.15, 0.05),
    "Premium": PricingPreset("Premium", 0.25, 0.15),
}
def load_presets() -> Dict[str, PricingPreset]:
    if PRESETS_FILE.exists():
        data = json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
        return {k: PricingPreset(**v) for k, v in data.items()}
    return DEFAULTS.copy()
def save_presets(presets: Dict[str, PricingPreset]) -> None:
    PRESETS_FILE.write_text(json.dumps({k: asdict(v) for k,v in presets.items()}, indent=2), encoding="utf-8")
