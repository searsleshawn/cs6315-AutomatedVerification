from dataclasses import dataclass
from typing import Dict, Any, List
import json

@dataclass
class TransitionSystem:
    """
    Represents a finite-state transition system.

    Attributes:
        name        : (str) Model name.
        states      : (List[str]) All possible states.
        init        : (str) Initial state of the system.
        transitions : (Dict[str, List[str]]) Maps each state to its possible successors.
        variables   : (Dict[str, Any]) Optional metadata (e.g., labels or properties).
    """
    name: str
    states: List[str]
    init: str
    transitions: Dict[str, List[str]]
    variables: Dict[str, Any] = None

    @staticmethod
    def from_json(path: str) -> "TransitionSystem":
        """
        Load a transition system from a JSON file.
        The JSON must define: states, init, and transitions.

        Example:
        {
            "name": "ToggleSystem",
            "states": ["s0", "s1"],
            "init": "s0",
            "transitions": {"s0": ["s1"], "s1": ["s0"]}
        }
        """
        with open(path, "r") as f:
            data = json.load(f)
        return TransitionSystem(
            name=data.get("name", "Unnamed"),
            states=data["states"],
            init=data["init"],
            transitions=data["transitions"],
            variables=data.get("variables", {})
        )
