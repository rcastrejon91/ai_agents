from __future__ import annotations

import json
import asyncio

import streamlit as st
import pandas as pd

from controller import AgentController

controller = AgentController(enable_memory=True)

st.title("AITaskFlo")

agent_name = st.selectbox("Choose an agent", list(controller.available_agents().keys()))
input_text = st.text_area("Input JSON", "{}")

if st.button("Run"):
    try:
        data = json.loads(input_text or "{}")
        result = asyncio.run(controller.route(agent_name, data))
        st.json(result)
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error("Error processing request")

if controller.memory:
    st.subheader("History")
    memory_data = controller.memory.fetch_all()
    for sid, entries in memory_data.items():
        st.write(f"Session {sid}:")
        for item in entries:
            st.json(item)

    # Simple data visualization of session activity
    session_counts = {sid: len(entries) for sid, entries in memory_data.items()}
    if session_counts:
        st.subheader("Session Activity")
        df = pd.DataFrame(list(session_counts.items()), columns=["session", "entries"]).set_index("session")
        st.bar_chart(df)

