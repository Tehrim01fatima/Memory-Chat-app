from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai

env_file = Path(__file__).with_name(".env")
if not env_file.exists():
    env_file = env_file.parent / "venv" / ".env"
load_dotenv(env_file)

MODEL = "gemini-2.5-flash"


@st.cache_resource
def get_client():
    return genai.Client()


def chat(user_message, history):
    contents = []
    for message in history:
        role = "model" if message["role"] == "assistant" else "user"
        contents.append(
            {"role": role, "parts": [{"text": message["content"]}]}
        )
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    response = get_client().models.generate_content(
        model=MODEL,
        contents=contents,
    )
    return response.text or "I couldn't generate a response. Please try again."


st.set_page_config(page_title="Memory Chat", page_icon="💬")
st.caption("A chat that remembers the conversation while this session is open.")

if "messages" not in st.session_state:
    st.session_state.messages = []

title_column, clear_column = st.columns([4, 1])
with title_column:
    st.title("Memory Chat")
with clear_column:
    st.write("")
    if st.button(
        "Clear conversation",
        icon=":material/delete_sweep:",
        disabled=not st.session_state.messages,
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_message := st.chat_input("Type your Message "):
    try:
        with st.spinner("Thinking..."):
            reply = chat(user_message, st.session_state.messages)
    except Exception as error:
        st.error(f"Gemini request failed: {error}")
    else:
        st.session_state.messages.extend(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": reply},
            ]
        )
        st.rerun()