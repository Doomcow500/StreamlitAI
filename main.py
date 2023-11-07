import streamlit as st
import openai
import uuid
import time
from openai import OpenAI

# Constants
MODEL = "gpt-4-1106-preview"
RETRY_LIMIT = 3
SHORT_DELAY = 1
LONG_DELAY = 3

# Initialize OpenAI client
client = OpenAI()

def initialize_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "run" not in st.session_state:
        st.session_state.run = {"status": None}
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "retry_error" not in st.session_state:
        st.session_state.retry_error = 0

def initialize_assistant():
    if "assistant" not in st.session_state:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        st.session_state.assistant = openai.beta.assistants.retrieve(st.secrets["OPENAI_ASSISTANT"])
        st.session_state.thread = client.beta.threads.create(metadata={'session_id': st.session_state.session_id})

def handle_run_status():
    if hasattr(st.session_state.run, 'status'):
        if st.session_state.run.status == "running":
            display_message('assistant', "Thinking ......", SHORT_DELAY)
        elif st.session_state.run.status == "failed":
            st.session_state.retry_error += 1
            if st.session_state.retry_error < RETRY_LIMIT:
                display_message('assistant', "Run failed, retrying ......", LONG_DELAY)
            else:
                st.error("FAILED: The OpenAI API is currently processing too many requests. Please try again later ......")
        elif st.session_state.run.status != "completed":
            st.session_state.run = client.beta.threads.runs.retrieve(thread_id=st.session_state.thread.id, run_id=st.session_state.run.id)
            if st.session_state.retry_error < RETRY_LIMIT:
                time.sleep(LONG_DELAY)
                st.rerun()

def display_message(role, message, delay):
    with st.chat_message(role):
        st.write(message)
    if st.session_state.retry_error < RETRY_LIMIT:
        time.sleep(delay)
        st.rerun()

# Main
initialize_session_state()
initialize_assistant()
handle_run_status()