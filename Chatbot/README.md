# FAQ Chatbot with Jira Integration

A Python-based chatbot that provides instant answers to FAQs about a specific topic (e.g., a company’s Product Lifecycle Management system). The knowledge base is customizable per company or use case.

This chatbot uses LangChain with Google Gemini for natural language understanding, Gradio for the frontend UI, ChromaDB as the vector database, and integrates with Jira to create and track tickets based on user issues.

---

## Features

- **Customizable Knowledge Base:** Easily adapt the chatbot knowledge base for different companies or domains.
- **Conversational FAQ:** Answer common questions using embeddings and semantic search.
- **Jira Ticket Creation:** Automatically create Jira tickets by asking for issue type, priority, and description.
- **Ticket Tracking:** Retrieve and display the Jira ticket ID after creation directly in the chat interface.
- **Modern Tech Stack:** Built with LangChain (Google Gemini), ChromaDB, Gradio, and Jira API.

---

## Technologies Used

- Python
- [LangChain](https://python.langchain.com/en/latest/)
- [Google Gemini LLM via LangChain](https://python.langchain.com/en/latest/modules/models/llms/integrations/google_generative_ai.html)
- [ChromaDB](https://www.trychroma.com/)
- [Gradio](https://gradio.app/)
- [Jira Python Library](https://jira.readthedocs.io/)
- python-dotenv for environment variable management

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/umair986/Gen_AI.git
cd Gen_AI/Chatbot
```

2. Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following environment variables:

```env
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USER=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=YOURPROJECT
GOOGLE_API_KEY=your_google_api_key
# Add any other required keys here
```

---

## Usage

1. Run the chatbot server:

```bash
python chatbot.py
```

2. Open the local Gradio URL (e.g., `http://localhost:7860`) in your browser.

3. Interact with the chatbot by asking FAQs related to your company’s domain.

4. To create a Jira ticket, the chatbot will prompt for:

- Issue type (e.g., Bug, Task)
- Priority (e.g., High, Medium)
- Description of the issue

5. After ticket creation, the chatbot will display the Jira ticket ID.

---

## Customizing the Knowledge Base

- Add or update documents in your knowledge base via the `knowledge_base.py` module.
- The chatbot uses embeddings stored in ChromaDB to semantically search your FAQ content.
- Customize documents per company or topic to improve chatbot accuracy.

---

## Contributing

Feel free to open issues or pull requests if you want to suggest improvements or report bugs.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
