import google.generativeai as genai
import os

def setup_gemini(api_key: str):
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)

def call_gemini(prompt: str, model_name="models/gemini-pro"):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        return f"Error calling Gemini: {e}"
