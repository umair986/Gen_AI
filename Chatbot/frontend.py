import gradio as gr
from chatbot_backend import get_answer, extract_ticket_fields, create_jira_ticket

# ---------- Main Message Handler ----------
def main_handler(message, chat_history, state):
    if state:  # We're in ticket creation mode
        fields = extract_ticket_fields(message)

        # Fallback: use original question as description if it's missing
        if fields and (not fields.get("description") or fields["description"].lower() == "no description provided"):
            fields["description"] = state.strip()

        if not fields or not fields.get("description"):
            chat_history.append((message, "❌ Couldn't parse ticket info. Please include description, priority (High/Medium/Low), and issue type (Bug/Task/Story)."))
            return "", chat_history, gr.update(visible=True), state

        issue_id = create_jira_ticket(fields)
        response = f"✅ Jira ticket created! Ticket ID: {issue_id}"
        chat_history.append((message, response))
        return "", chat_history, gr.update(visible=False), None

    # Normal chatbot response
    response = get_answer(message)
    chat_history.append((message, response))

    if "I don't know" in response or "I'm not sure" in response:
        chat_history.append(("🤖", "Would you like to raise a Jira ticket for this question?"))
        return "", chat_history, gr.update(visible=True), message  # Save original question in state

    return "", chat_history, gr.update(visible=False), None

# ---------- Dropdown Handler ----------
def handle_dropdown(choice, chat_history, state):
    if choice == "Yes":
        chat_history.append((
            "Proceeding to ticket creation.",
            "Please provide: description, priority (High/Medium/Low), and issue type (Bug/Task/Story)."
        ))
        return chat_history, gr.update(visible=True)
    else:
        chat_history.append((
            "Ticket creation cancelled.",
            "Let me know if you need anything else."
        ))
        return chat_history, gr.update(visible=False)

# ---------- Gradio UI ----------
with gr.Blocks() as demo:
    gr.Markdown("## 💬 Gemini Chatbot with Jira Integration")

    chatbot = gr.Chatbot()
    user_input = gr.Textbox(placeholder="Ask a question...")
    ticket_dropdown = gr.Dropdown(["Yes", "No"], label="Raise a Jira Ticket?", visible=False)
    submit_btn = gr.Button("Submit Ticket", visible=False)
    state = gr.State()

    # Submit when user presses Enter
    user_input.submit(
        main_handler,
        inputs=[user_input, chatbot, state],
        outputs=[user_input, chatbot, ticket_dropdown, state]
    )

    # Show Submit button when "Yes" is selected
    ticket_dropdown.change(
        handle_dropdown,
        inputs=[ticket_dropdown, chatbot, state],
        outputs=[chatbot, submit_btn]
    )

    # Submit ticket manually
    submit_btn.click(
        main_handler,
        inputs=[user_input, chatbot, state],
        outputs=[user_input, chatbot, ticket_dropdown, state]
    )

# ---------- Launch ----------
if __name__ == "__main__":
    demo.launch()
