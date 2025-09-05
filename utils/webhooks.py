from dataclasses import dataclass, asdict
from typing import Dict, Any
import json
@dataclass
class Event:
    name: str
    payload: Dict[str, Any]
def compile_event(name: str, payload: Dict[str, Any]) -> str:
    evt = Event(name=name, payload=payload)
    return json.dumps(asdict(evt), indent=2)
