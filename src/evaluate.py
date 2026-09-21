from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from orchestrator import MultiDomainOrchestrator, TOOL_DOMAINS


def evaluate(json_path: str | Path, output_dir: str | Path = "results") -> dict:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    dialogue_count = len(data)
    turn_count = 0
    schema_failures = 0
    tool_domain_acts = 0
    state_updates = 0
    domain_handoffs = 0
    no_booking_turns = 0
    multi_domain_dialogues = 0
    domain_counts = Counter()
    turn_lengths = []

    for dialogue in data.values():
        orchestrator = MultiDomainOrchestrator()
        seen_domains = set()
        turn_lengths.append(len(dialogue))
        for turn_id in sorted(dialogue, key=lambda x: int(x)):
            turn_count += 1
            payload = dialogue[turn_id]
            acts = payload.get("dialog_act", {})
            if not isinstance(acts, dict):
                schema_failures += 1
                continue
            try:
                result = orchestrator.process_turn(acts)
            except Exception:
                schema_failures += 1
                continue

            for act, slot_values in acts.items():
                if "-" not in act:
                    continue
                domain, intent = act.split("-", 1)
                if domain in TOOL_DOMAINS:
                    tool_domain_acts += 1
                    domain_counts[domain] += 1
                    seen_domains.add(domain)
                if intent.lower() == "nobook":
                    no_booking_turns += 1
                for pair in slot_values or []:
                    if isinstance(pair, list) and len(pair) >= 2:
                        slot, value = str(pair[0]), str(pair[1])
                        if slot not in {"none", ""} and value not in {"none", "?", ""}:
                            state_updates += 1

            domain_handoffs = domain_handoffs + (
                result["state"]["handoffs"] - domain_handoffs
                if result["state"]["handoffs"] > domain_handoffs else 0
            )

        if len(seen_domains) >= 2:
            multi_domain_dialogues += 1

    # Recompute handoffs exactly at dataset level to avoid cross-dialogue state.
    domain_handoffs = 0
    for dialogue in data.values():
        previous = None
        for turn_id in sorted(dialogue, key=lambda x: int(x)):
            domains = []
            for act in dialogue[turn_id].get("dialog_act", {}):
                domain = act.split("-", 1)[0] if "-" in act else ""
                if domain in TOOL_DOMAINS:
                    domains.append(domain)
            current = domains[0] if domains else previous
            if current and previous and current != previous:
                domain_handoffs += 1
            if current:
                previous = current

    metrics = {
        "dialogues": dialogue_count,
        "turns": turn_count,
        "mean_turns": round(sum(turn_lengths) / dialogue_count, 2),
        "domains": len(domain_counts),
        "multi_domain_dialogues": multi_domain_dialogues,
        "multi_domain_rate": round(multi_domain_dialogues / dialogue_count, 4),
        "tool_domain_acts": tool_domain_acts,
        "state_updates": state_updates,
        "domain_handoffs": domain_handoffs,
        "no_booking_turns": no_booking_turns,
        "schema_failures": schema_failures,
    }

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    with (out / "domain_counts.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "act_count"])
        for domain, count in domain_counts.most_common():
            writer.writerow([domain, count])
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path")
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()
    evaluate(args.json_path, args.output_dir)
