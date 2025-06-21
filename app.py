from __future__ import annotations

import json
import asyncio

import streamlit as st

from controller import AgentController

controller = AgentController(enable_memory=True)

st.title("AITaskFlo")

available_agents = list(controller.available_agents().keys())
agent_name = st.selectbox("Choose an agent", available_agents)
input_text = st.text_area("Input JSON", "{}")

if st.button("Run"):
    try:
        data = json.loads(input_text or "{}")
        result = asyncio.run(controller.route(agent_name, data))
        st.json(result)
    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Error processing request: {exc}")

if controller.memory:
    st.subheader("History")
    for sid, entries in controller.memory.fetch_all().items():
        st.write(f"Session {sid}:")
        for item in entries:
            st.json(item)
