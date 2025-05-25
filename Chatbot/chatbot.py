import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API")

vectordb = Chroma(
    persist_directory="db",
    embedding_function= None
)

retriever = vectordb.as_retriever(search_kwargs={"k": 3})

llm = ChatGoogleGenerativeAI(
    model="models/chat-bison-001",
    google_api_key= api_key,
    temperature = 0.2
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

qa_chain = ConversationalRetrievalChain.from_LLM(
    llm,
    retriever,
    memory=memory,
    return_source_documents=False
)

def get_answer(user_query:str) -> str:
    """
    Given a user question, runs the retrieval+LLM chain
    and returns the assistant's answer.
    """
    chain_input = {"question": user_query, "chat_history": []}
    result = qa_chain(chain_input)
    return result["answer"]