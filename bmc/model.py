from dataclasses import dataclass
from typing import Dict, Any, List
import json

@dataclass
class TransitionSystem:
    name: str
    states: List[str]
    init: str
    transitions: Dict[str, List[str]]
    variables: Dict[str, Any] = None

    @staticmethod
    def from_json(path: str) -> "TransitionSystem":
        """Load transition system from a JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return TransitionSystem(
            name=data.get("name", "Unnamed"),
            states=data["states"],
            init=data["init"],
            transitions=data["transitions"],
            variables=data.get("variables", {})
        )
