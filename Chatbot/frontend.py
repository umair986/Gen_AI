import gradio as gr
from chatbot_backend import get_answer, extract_ticket_fields, create_jira_ticket

def main_handler(message, chat_history, state):
    if state:  # expecting ticket fields
        fields = extract_ticket_fields(message)
        if not fields:
            chat_history.append((message, "❌ Couldn't parse ticket info. Please include description, priority (High/Medium/Low), and issue type (Bug/Task/Story)."))
            return "", chat_history, gr.update(visible=True), state  # keep state for retry

        issue_id = create_jira_ticket(fields)
        response = f"✅ Jira ticket created successfully! Ticket ID: {issue_id}"
        chat_history.append((message, response))
        return "", chat_history, gr.update(visible=False), None  # reset state

    # Not expecting ticket info – normal Q&A flow
    response = get_answer(message)
    chat_history.append((message, response))
    
    if "I don't know" in response or "I'm not sure" in response:
        return "", chat_history, gr.update(visible=True), message  # store question as state

    return "", chat_history, gr.update(visible=False), None

def handle_dropdown(choice, chat_history, state):
    if choice == "Yes":
        instruction = "Please describe the issue with **description**, **priority** (High/Medium/Low), and **issue type** (Bug/Task/Story)."
        chat_history.append(("✅ Proceeding to ticket creation.", instruction))
        return chat_history, gr.update(visible=False)
    else:
        chat_history.append(("User selected No", "No problem. Let me know if you need anything else."))
        return chat_history, gr.update(visible=False)

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 💬 Gemini Chatbot with Jira Integration")

    chatbot = gr.Chatbot(type="tuple", height=400)
    user_input = gr.Textbox(placeholder="Type your question here...", submit_btn=True)
    ticket_dropdown = gr.Dropdown(choices=["Yes", "No"], label="Raise a Jira Ticket?", visible=False)
    state = gr.State()

    user_input.submit(
        main_handler,
        inputs=[user_input, chatbot, state],
        outputs=[user_input, chatbot, ticket_dropdown, state]
    )

    ticket_dropdown.change(
        handle_dropdown,
        inputs=[ticket_dropdown, chatbot, state],
        outputs=[chatbot, ticket_dropdown]
    )

if __name__ == "__main__":
    demo.launch()
