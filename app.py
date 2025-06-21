from __future__ import annotations

import json
import asyncio

import streamlit as st

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
    for row in controller.memory.fetch_all():
        st.write(row)

