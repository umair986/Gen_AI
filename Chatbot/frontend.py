import gradio as gr
from chatbot_backend import get_answer

def respond(message, chat_history):
    response = get_answer(message)
    chat_history.append((message,response))
    if "I don't know" in response:
        return "" , chat_history, gr.Dropdown(visible=True),message
    return "", chat_history , gr.Dropdown(visible=False), None

with gr.Blocks() as demo :
    chatbot = gr.Chatbot(type= "tuple", height=400)
    user_Input = gr.Textbox(placeholder="Type your question here..", submit_btn=True)
    ticket_dropdown = gr.Dropdown(choices=["Yes","No"], label="Raise a Jira Ticket?", visible=False)
    user_Input.submit(
        respond, 
        inputs=[user_Input, chatbot, ticket_dropdown], 
        outputs=[user_Input, chatbot, ticket_dropdown, gr.State()]
    )