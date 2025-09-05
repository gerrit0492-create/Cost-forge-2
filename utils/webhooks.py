import json
from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class Event:
    name: str
    payload: Dict[str, Any]


def compile_event(name: str, payload: Dict[str, Any]) -> str:
    evt = Event(name=name, payload=payload)
    return json.dumps(asdict(evt), indent=2)
