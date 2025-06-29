from src.ui.streamlit_ui import StreamlitFastAPIChatBot

chatbot = StreamlitFastAPIChatBot(api_url="http://127.0.0.1:8000/message")
chatbot.run()
