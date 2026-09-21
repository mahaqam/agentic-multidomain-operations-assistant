import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestrator import MultiDomainOrchestrator

st.set_page_config(
    page_title="Agentic Multi-Domain Operations Assistant",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Agentic Multi-Domain Operations Assistant")
st.caption("Stateful multi-domain tool orchestration using structured MultiWOZ-style dialogue acts.")

if "agent" not in st.session_state:
    st.session_state.agent = MultiDomainOrchestrator()

SAMPLES = {
    "Hotel search": {
        "Hotel-Inform": [["area", "centre"], ["pricerange", "cheap"]],
        "Hotel-Request": [["parking", "?"]],
    },
    "Restaurant request": {
        "Restaurant-Inform": [["area", "north"], ["food", "italian"]],
        "Restaurant-Request": [["phone", "?"]],
    },
    "Train planning": {
        "Train-Inform": [["departure", "cambridge"], ["destination", "london"], ["day", "monday"]],
        "Train-Request": [["arriveby", "?"]],
    },
    "Booking recovery": {
        "Booking-NoBook": [["none", "none"]],
    },
}

with st.sidebar:
    st.header("About this demo")
    st.write(
        "This site demonstrates state persistence, structured tool calls, domain handoffs, and recovery signals."
    )
    st.markdown("[View source on GitHub](https://github.com/mahaqam/agentic-multidomain-operations-assistant)")
    if st.button("Reset conversation state", use_container_width=True):
        st.session_state.agent.reset()
        st.success("State reset")

sample_name = st.selectbox("Choose an example", list(SAMPLES))
default_json = json.dumps(SAMPLES[sample_name], indent=2)
raw = st.text_area(
    "Dialogue act JSON",
    value=default_json,
    height=210,
    help="Edit the structured acts, then process the turn. State persists between turns until reset.",
)

if st.button("Process turn", type="primary", use_container_width=True):
    try:
        acts = json.loads(raw)
        result = st.session_state.agent.process_turn(acts)
        left, right = st.columns(2)
        with left:
            st.subheader("Tool calls")
            st.json(result["tool_calls"])
        with right:
            st.subheader("Conversation state")
            st.json(result["state"])
        if result["recovery_needed"]:
            st.warning("Recovery / human-escalation path recommended for this turn.")
        else:
            st.success("Turn processed successfully.")
    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON: {exc}")
    except Exception as exc:
        st.error(str(exc))

st.divider()
metrics = st.columns(4)
metrics[0].metric("Dialogues replayed", "10,437")
metrics[1].metric("Annotated turns", "143,044")
metrics[2].metric("Multi-domain dialogues", "78.3%")
metrics[3].metric("Schema failures", "0")

st.markdown("### What the prototype demonstrates")
st.write(
    "Each structured dialogue act is mapped to a tool-domain action, concrete slot values are persisted in session state, "
    "domain changes are tracked as handoffs, and booking failures trigger a recovery signal."
)
st.info(
    "Verified replay: 144,047 tool-domain acts and 195,066 state updates across the full uploaded dataset."
)
st.warning(
    "Scope: the uploaded dataset contains structured dialogue acts rather than raw user utterances. "
    "This validates orchestration/state handling, not end-to-end LLM understanding or learned tool selection."
)
