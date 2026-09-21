from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.orchestrator import MultiDomainOrchestrator

app = FastAPI(title="Agentic Multi-Domain Operations Assistant")
_sessions: dict[str, MultiDomainOrchestrator] = {}


class TurnRequest(BaseModel):
    session_id: str = Field(default="demo")
    dialog_act: dict[str, list[list[str]]]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/turn")
def process_turn(payload: TurnRequest):
    agent = _sessions.setdefault(payload.session_id, MultiDomainOrchestrator())
    return agent.process_turn(payload.dialog_act)


@app.delete("/session/{session_id}")
def reset_session(session_id: str):
    _sessions.pop(session_id, None)
    return {"reset": True, "session_id": session_id}
