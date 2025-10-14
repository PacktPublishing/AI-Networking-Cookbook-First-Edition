from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Previous setup code (OpenAI, database, etc.)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
    if not client.api_key:
        return "Please set your OPENAI_API_KEY environment variable"
    
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

# Web interface endpoint
@app.get("/", response_class=HTMLResponse)
def web_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; max-width: 800px; }
            .form-group { margin: 20px 0; }
            input[type="text"], select, textarea { width: 100%; padding: 10px; font-size: 16px; }
            button { background: #007cba; color: white; padding: 12px 24px; border: none; font-size: 16px; cursor: pointer; }
            .answer { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🤖 Network AI Assistant</h1>
        <form method="post" action="/web-ask">
            <div class="form-group">
                <label>Ask your network question:</label>
                <textarea name="question" rows="3" placeholder="e.g., How do I troubleshoot BGP neighbor down?"></textarea>
            </div>
            <div class="form-group">
                <label>Device Type:</label>
                <select name="device_type">
                    <option value="generic">Generic</option>
                    <option value="cisco">Cisco</option>
                    <option value="juniper">Juniper</option>
                    <option value="arista">Arista</option>
                    <option value="palo alto">Palo Alto</option>
                </select>
            </div>
            <button type="submit">Get AI Answer</button>
        </form>
        
        <div>
            <h3>Recent Questions</h3>
            <p><a href="/history">View all conversation history →</a></p>
        </div>
    </body>
    </html>
    """

# Handle web form submission
@app.post("/web-ask", response_class=HTMLResponse)
def web_ask_question(question: str = Form(...), device_type: str = Form("generic")):
    answer = get_ai_answer(question, device_type)
    
    # Save to database
    session = Session()
    session.add(Question(question=question, answer=answer, device_type=device_type))
    session.commit()
    session.close()
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network AI Assistant</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; max-width: 800px; }}
            .question {{ background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .answer {{ background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 5px; white-space: pre-wrap; }}
            .back {{ margin: 20px 0; }}
            a {{ color: #007cba; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h1>🤖 Network AI Assistant</h1>
        
        <div class="question">
            <strong>Your Question ({device_type}):</strong><br>
            {question}
        </div>
        
        <div class="answer">
            <strong>AI Answer:</strong><br>
            {answer}
        </div>
        
        <div class="back">
            <a href="/">← Ask Another Question</a> | 
            <a href="/history">View History</a>
        </div>
    </body>
    </html>
    """

# Keep existing API endpoints
@app.post("/ask")
def ask_question(request: QuestionRequest):
    answer = get_ai_answer(request.question, request.device_type)
    
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
    