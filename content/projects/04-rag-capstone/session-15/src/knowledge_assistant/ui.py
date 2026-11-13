"""A minimal web UI. Run it with:  uv run streamlit run src/knowledge_assistant/ui.py

What the page must do (Milestone 4; tests/acceptance/test_ui.py checks each point):

- A text input labelled "Question" and a button labelled "Ask".
- On Ask with a blank question: a warning (st.warning or st.info), and no assistant call.
- On Ask: the answer and, under it, each cited source as "[n] citation".
- When the documentation doesn't cover the question: the "not found" message.
- When something goes wrong (any AssistantError, including a missing key or an index
  built with other settings): st.error with the error's message, never a traceback.
- Build the assistant once, with st.cache_resource, not on every rerun: Streamlit runs
  this whole script again on every interaction, and building the assistant loads the
  embedding model and opens the index.
"""

import streamlit as st

from knowledge_assistant.assistant import Assistant, build_assistant  # noqa: F401
from knowledge_assistant.errors import AssistantError, GenerationError  # noqa: F401

st.title("Internal Knowledge Assistant")

# TODO Milestone 4
st.info("Not built yet: see Milestone 4 of the Session 15 workbook.")
