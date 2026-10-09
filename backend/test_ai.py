from dotenv import load_dotenv
load_dotenv()
import os
from google import genai

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
response = client.models.generate_content(
    model='gemini-3.5-flash-lite',
    contents='Say hello'
)
print(response.text)