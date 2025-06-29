import streamlit as st
import requests
import re

from src.constants import  CONSTANT_streamlit_ui_title


class StreamlitFastAPIChatBot:
    def __init__(self, api_url="http://127.0.0.1:8000/message"):
        self.api_url = api_url
        self._setup()

    def _setup(self):
        st.set_page_config(page_title=f"🤖 {CONSTANT_streamlit_ui_title}", layout="centered")
        st.title(f"🤖 {CONSTANT_streamlit_ui_title}")
        st.markdown("###### Hello! I'm your assistant powered by FastAPI. Ask me anything!")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

    def send_message(self, user_input):
        # Append user message
        st.session_state.chat_history.append(("user", user_input))

        try:
            response = requests.post(
                self.api_url,
                json={"user_message": user_input},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                bot_reply = data["data"]["messages"][-1]["content"]
                bot_reply = re.sub(r"<think>.*?</think>", "", bot_reply, flags=re.DOTALL).strip()
            else:
                bot_reply = f"❌ Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            bot_reply = f"⚠️ Request failed: {str(e)}"

        # Append bot response
        st.session_state.chat_history.append(("bot", bot_reply))

    def display_chat_history(self):
        for sender, message in st.session_state.chat_history:
            with st.chat_message("user" if sender == "user" else "ai"):
                st.markdown(message)

    def run(self):
        self.display_chat_history()

        user_input = st.chat_input("Ask me anything...")
        if user_input:
            # Show user's message
            st.chat_message("user").markdown(user_input)
            self.send_message(user_input)

            # Show bot's message (latest one)
            last_bot_message = st.session_state.chat_history[-1][1]
            st.chat_message("ai").markdown(last_bot_message)

