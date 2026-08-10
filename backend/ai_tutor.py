import os
import requests
import json

# You can use Gemini API (Free tier available)
# Or OpenAI API with your key

class AITutor:
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        # Use API key if provided, else use fallback
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
    
    def ask(self, question, context=""):
        """Ask the AI tutor a question about a course"""
        if not self.api_key:
            return "⚠️ API key not set. Please add GEMINI_API_KEY to environment variables."
        
        prompt = f"""
        You are LearnVerse AI Tutor, a helpful teaching assistant.
        
        Context: {context}
        
        Student Question: {question}
        
        Please provide a clear, concise, and educational answer.
        """
        
        try:
            response = requests.post(
                self.base_url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"⚠️ Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"