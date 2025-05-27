import os
import re
from jira import JIRA
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API")

# 1. Set up Vector DB retriever
vectordb = Chroma(
    persist_directory="db",
    embedding_function=None  # Already embedded
)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

# 2. Set up LLM
llm = ChatGoogleGenerativeAI(
    model="models/chat-bison-001",
    google_api_key=api_key,
    temperature=0.2
)

# 3. Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's question based only on the following context. If you don't know, say you don't know.\n\nContext:\n{context}"),
    ("human", "{question}")
])

# 4. Retrieval + Prompt + LLM Chain (stateless version)
retrieval_chain = (
    RunnableMap({
        "context": lambda x: retriever.invoke(x["question"]),
        "question": lambda x: x["question"]
    })
    | prompt
    | llm
    | StrOutputParser()
)

# 5. Memory Wrapper (optional for stateful use)
chat_history = []

def get_answer(user_query: str, use_memory=True) -> str:
    global chat_history

    if use_memory:
        # Combine last messages for richer context
        combined_history = "\n".join([
            f"Human: {m.content}" if isinstance(m, HumanMessage) else f"AI: {m.content}"
            for m in chat_history[-5:]  # last 5 exchanges
        ])
        input_question = f"{combined_history}\nHuman: {user_query}"
    else:
        input_question = user_query

    answer = retrieval_chain.invoke({"question": input_question})

    if use_memory:
        chat_history.append(HumanMessage(content=user_query))
        chat_history.append(AIMessage(content=answer))

    return answer

def extract_ticket_fields(message:str)-> dict:
    # Extracts description, priority, and issue type from the user's message.
    priority_match = re.search(r"\b(high|medium|low)\b", message, re.IGNORECASE)
    type_match = re.search(r"\b(high|medium|low)\b", message, re.IGNORECASE)

    description = message.strip()  # Use the entire message minus matched keywords as description fallback

    if priority_match and type_match:
        return{
            "description" : description,
            "priority" : priority_match.group(1).capitalize(),
            "issue_type" : type_match.group(1).capitalize()
        }
    return None #if nothing is found

def create_jira_ticket(fields : dict) -> str:
    # Creates a Jira ticket using provided fields and returns the issue ID.
    jira = JIRA(
        server = os.getenv("JIRA_URL"),
        basic_auth = (os.getenv("JIRA_USER"), os.getenv("JIRA_API_TOKEN"))
    )

    issue_dict = {
        'project': {'key': os.getenv("JIRA_PROJECT_KEY")},
        'summary': fields['description'][:50],  # Truncated summary
        'description': fields['description'],
        'issuetype': {'name': fields['issue_type']},
        'priority': {'name': fields['priority']}
    }

    issue = jira.create_issue(fields=issue_dict)
    return issue.key