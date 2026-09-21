from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TOOL_DOMAINS = {"Hotel", "Restaurant", "Train", "Attraction", "Taxi", "Booking", "Hospital", "Police"}


@dataclass
class AgentState:
    slots: dict[str, dict[str, str]] = field(default_factory=dict)
    active_domain: str | None = None
    handoffs: int = 0
    turns: int = 0


class MultiDomainOrchestrator:
    """Stateful dispatcher for annotated MultiWOZ-style dialogue acts."""

    def __init__(self):
        self.state = AgentState()

    def _update_slot(self, domain: str, slot: str, value: str) -> None:
        if slot in {"none", ""} or value in {"none", "?", ""}:
            return
        self.state.slots.setdefault(domain, {})[slot] = value

    def process_turn(self, dialog_act: dict[str, list[list[str]]]) -> dict[str, Any]:
        self.state.turns += 1
        tool_calls = []
        recovery_needed = False

        for act, slot_values in dialog_act.items():
            if "-" not in act:
                continue
            domain, intent = act.split("-", 1)
            if domain not in TOOL_DOMAINS:
                continue

            if self.state.active_domain and self.state.active_domain != domain:
                self.state.handoffs += 1
            self.state.active_domain = domain

            payload = {}
            for pair in slot_values or []:
                if isinstance(pair, list) and len(pair) >= 2:
                    slot, value = str(pair[0]), str(pair[1])
                    payload[slot] = value
                    self._update_slot(domain, slot, value)

            if intent.lower() == "nobook":
                recovery_needed = True

            tool_calls.append({
                "tool": domain.lower(),
                "intent": intent,
                "arguments": payload,
            })

        return {
            "tool_calls": tool_calls,
            "recovery_needed": recovery_needed,
            "state": {
                "active_domain": self.state.active_domain,
                "slots": self.state.slots,
                "handoffs": self.state.handoffs,
                "turns": self.state.turns,
            },
        }

    def reset(self) -> None:
        self.state = AgentState()
