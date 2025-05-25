import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import json
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API")
print(api_key)

# Initialize embedding model
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", 
    google_api_key=api_key
)

# Setup Chroma vector store with persistence
persist_directory = "db"
vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_model,
    collection_name="knowledge_base",  # Optional: name the collection
)

# Load JSON data
with open("Chatbot/python_faq.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

# Extract actual FAQ list
faq_list = faq_data["faqs"]

# Convert each FAQ to a LangChain Document
documents = [
    Document(page_content=f"Q: {item['question']}\nA: {item['answer']}")
    for item in faq_list
]

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# Save to Chroma
vectordb.add_documents(docs)

print("Documents Saved to Chroma ✅")
