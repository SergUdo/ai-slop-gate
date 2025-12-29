# test_gemini.py
import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Hello, world!")
print("Response:", response.text)

