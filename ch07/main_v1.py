from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI(title="Network AI")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not client.api_key:
        return {"answer": "Please set your OPENAI_API_KEY environment variable"}
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a network engineer assistant. Give concise, practical answers about network troubleshooting, configuration, and performance issues."},
                {"role": "user", "content": request.question}
            ],
            max_tokens=150
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        return {"answer": f"AI service unavailable: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)