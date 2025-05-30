import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    print("Error: GOOGLE_API_KEY not found. Please set it in your environment or .env file.")
else:
    try:
        genai.configure(api_key=google_api_key)

        print("Available models that support 'generateContent' (for chat/text generation):")
        count = 0
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name} (Display Name: {m.display_name}, Version: {m.version})")
                # You can print other attributes too:
                # print(f"  Description: {m.description}")
                # print(f"  Input Token Limit: {m.input_token_limit}")
                # print(f"  Output Token Limit: {m.output_token_limit}")
                # print(f"  Supported Generation Methods: {m.supported_generation_methods}")
                count += 1
        
        if count == 0:
            print("\nNo models found that support 'generateContent'.")
            print("This could mean:")
            print("1. Your API key might not have the 'Generative Language API' enabled or correctly configured in Google Cloud.")
            print("2. There might be regional restrictions or temporary issues.")
            print("3. Double-check your API key.")

        print("\n---")
        print("Available models that support 'embedContent' (for embeddings):")
        embed_count = 0
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"- {m.name} (Display Name: {m.display_name}, Version: {m.version})")
                embed_count += 1
        if embed_count == 0:
            print("No models found that support 'embedContent'.")


    except Exception as e:
        print(f"An error occurred while trying to list models: {e}")
        print("Please ensure your GOOGLE_API_KEY is correct and has the 'Generative Language API' enabled in your Google Cloud project.")
        print("Also, check your internet connection.")