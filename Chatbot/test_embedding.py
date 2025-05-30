# In your test_embedding.py or wherever 'embedding' is defined
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# THIS IS THE CRUCIAL PART
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)

# Then your failing line:
result = embedding.embed_query("Hello world")
print(result)