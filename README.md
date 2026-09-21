# Agentic Multi-Domain Operations Assistant

[Live Demo](https://agentic-multidomain-operations-assistant.streamlit.app/)

Stateful tool-orchestration prototype evaluated on the uploaded MultiWOZ 2.2 `dialog_acts.json` annotations.

## Dataset
- 10,437 dialogues
- 143,044 annotated turns
- 8 operational domains: Hotel, Restaurant, Train, Attraction, Taxi, Booking, Hospital, Police
- 78.3% of dialogues touch at least two tool domains

## What the project does
The assistant replays structured dialogue acts through a state manager, dispatches domain-specific tool calls, preserves slot values across turns, tracks domain handoffs, and exposes the orchestration layer through FastAPI. The evaluation is intentionally based on annotated dialogue acts because the uploaded file does not contain raw utterance text.

## Verified replay / orchestration results
- 143,044 turns replayed
- 144,047 domain tool acts dispatched
- 195,066 state updates applied
- 32,433 domain handoffs observed
- 1,320 booking-failure (`NoBook`) turns identified as recovery opportunities
- **0 schema failures** while replaying the uploaded annotations

These are workflow-replay and engineering validation metrics, not LLM reasoning accuracy.

## Files
- `src/orchestrator.py` — state memory, tool routing, handoff tracking
- `src/evaluate.py` — full-dataset replay benchmark
- `api/app.py` — FastAPI orchestration endpoint
- `app/dashboard.py` — Streamlit demo using structured dialogue acts
- `results/metrics.json` — verified summary
- `results/domain_counts.csv` — tool-domain counts

## Run
```bash
pip install -r requirements.txt
python src/evaluate.py dialog_acts.json
uvicorn api.app:app --reload
streamlit run app/dashboard.py
```

## Limitations
- The uploaded `dialog_acts.json` contains structured dialogue acts and slot annotations, but not the original natural-language utterances. This project therefore validates state management, tool selection from annotated acts, orchestration, and failure handling rather than end-to-end natural-language agent reasoning.
- Production use would require an NLU/LLM layer, confidence thresholds, tool authorization, privacy controls, observability, regression suites, and human escalation.
