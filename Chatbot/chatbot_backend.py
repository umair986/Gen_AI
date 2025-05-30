import os
import re
import logging
from jira import JIRA
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

# ---------- Setup ----------
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variable check
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# ---------- Embedding + Retrieval ----------
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=api_key
)

vectordb = Chroma(
    persist_directory="Chatbot/db",
    embedding_function=embedding_model,
    collection_name="knowledge_base"
)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

# ---------- LLM Setup ----------
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash-latest",
    google_api_key=api_key,
    temperature=0.2
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's question based only on the following context. If you don't know, say you don't know.\n\nContext:\n{context}"),
    ("human", "{question}")
])

retrieval_chain = (
    RunnableMap({
        "context": lambda x: retriever.invoke(x["question"]),
        "question": lambda x: x["question"]
    })
    | prompt
    | llm
    | StrOutputParser()
)

# ---------- Chat Memory ----------
chat_history = []

def reset_chat_history():
    global chat_history
    chat_history = []

# ---------- Answer Generation ----------
def get_answer(user_query: str, use_memory=True) -> str:
    global chat_history

    if use_memory:
        combined_history = "\n".join([
            f"Human: {m.content}" if isinstance(m, HumanMessage) else f"AI: {m.content}"
            for m in chat_history[-5:]
        ])
        input_question = f"{combined_history}\nHuman: {user_query}"
    else:
        input_question = user_query

    try:
        logger.info(f"Processing: {input_question}")
        answer = retrieval_chain.invoke({"question": input_question})
        logger.info(f"Answer: {answer}")
    except Exception as e:
        logger.error(f"Retrieval chain error: {e}")
        answer = "Sorry, I encountered an error while searching for the answer."

    if use_memory:
        chat_history.append(HumanMessage(content=user_query))
        chat_history.append(AIMessage(content=answer))

    return answer

# ---------- Jira Ticket Field Extraction ----------
def extract_ticket_fields(message: str) -> dict:
    priority_match = re.search(r"\b(high|medium|low)\b", message, re.IGNORECASE)
    type_match = re.search(r"\b(bug|task|story)\b", message, re.IGNORECASE)

    if not (priority_match and type_match):
        return None

    priority = priority_match.group(1).capitalize()
    issue_type = type_match.group(1).capitalize()

    issue_type_ids = {
        "Bug": "10068",
        "Task": "10069",
        "Story": "10070"
    }

    description_text = re.sub(
        r"\b(high|medium|low|bug|task|story)\b", "", message, flags=re.IGNORECASE
    ).strip()

    return {
        "description": description_text or "No description provided",
        "priority": priority,
        "issue_type": issue_type,
        "issue_type_id": issue_type_ids.get(issue_type)
    }

# ---------- Jira Ticket Creation ----------
def create_jira_ticket(fields: dict) -> str:
    try:
        jira = JIRA(
            server=os.getenv("JIRA_URL"),
            basic_auth=(os.getenv("JIRA_USER"), os.getenv("JIRA_API_TOKEN"))
        )

        
        issue_dict = {
                 "project": {"key": os.getenv("JIRA_PROJECT_KEY")},
                 "summary": fields["description"][:50],
                 "description": fields["description"],  # plain string now
                "issuetype": {"id": fields["issue_type_id"]},
                "priority": {"name": fields["priority"]}
        }

        issue = jira.create_issue(fields=issue_dict)
        logger.info(f"Jira Ticket Created: {issue.key}")
        return issue.key
    except Exception as e:
        logger.error(f"Failed to create Jira ticket: {e}")
        return "Failed to create Jira ticket. Please try again later."
