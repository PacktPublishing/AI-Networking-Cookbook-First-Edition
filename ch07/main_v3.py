from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# OpenAI setup
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database setup
engine = create_engine("sqlite:///questions.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    device_type = Column(String)
    timestamp = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)
app = FastAPI(title="Network AI")

class QuestionRequest(BaseModel):
    question: str
    device_type: str = "generic"

def get_ai_answer(question: str, device_type: str = "generic"):
    """Get answer from OpenAI with device context"""
    if not client.api_key:
        return "Please set your OPENAI_API_KEY environment variable"
    
    # Build device-specific system prompt
    system_msg = "You are a network engineer assistant. "
    if device_type.lower() == "cisco":
        system_msg += "Focus on Cisco IOS/IOS-XE commands. "
    elif device_type.lower() == "juniper":
        system_msg += "Focus on Junos commands. "
    elif device_type.lower() == "arista":
        system_msg += "Focus on Arista EOS commands. "
    elif device_type.lower() == "palo alto":
        system_msg += "Focus on Palo Alto firewall commands. "
    system_msg += "Give concise, practical answers with specific commands."
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": question}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI service unavailable: {str(e)}"

@app.post("/ask")
def ask_question(request: QuestionRequest):
    answer = get_ai_answer(request.question, request.device_type)
    
    # Save to database
    session = Session()
    session.add(Question(question=request.question, answer=answer, device_type=request.device_type))
    session.commit()
    session.close()
    
    return {"answer": answer, "device_type": request.device_type}

@app.get("/history")
def get_history():
    session = Session()
    questions = session.query(Question).order_by(Question.timestamp.desc()).limit(10).all()
    session.close()
    return [{"question": q.question, "answer": q.answer, "device_type": q.device_type, "time": q.timestamp} for q in questions]

@app.get("/devices")
def supported_devices():
    return {
        "supported_devices": ["cisco", "juniper", "arista", "palo alto", "generic"],
        "usage": "Include device_type in your JSON request for device-specific help"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)