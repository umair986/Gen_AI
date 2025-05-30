import os
import json
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API")

# Initialize embedding model
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=api_key
)

# Define persistence directory and collection name
persist_directory = "Chatbot/db"
collection_name = "knowledge_base"

# Initialize Chroma vector store
vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_model,
    collection_name=collection_name
)

# Load and parse the FAQ JSON file
faq_path = "Chatbot/PLM_KB_flat.json"
with open(faq_path, "r", encoding="utf-8") as f:
    faq_data = json.load(f)

# Extract FAQ items
faq_list = faq_data.get("faqs", [])

# Convert each item to LangChain Document
documents = [
    Document(page_content=f"Q: {item['question']}\nA: {item['answer']}")
    for item in faq_list
]

# Split documents into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = text_splitter.split_documents(documents)

# Add documents to Chroma DB
vectordb.add_documents(split_docs)

print("✅ Documents successfully saved to Chroma.")

