import gradio as gr
from chatbot_backend import get_answer

def respond(message, chat_history):
    response = get_answer(message)
    chat_history.append((message,response))
    return "" , chat_history