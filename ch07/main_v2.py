from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI(title="Network AI")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QuestionRequest(BaseModel):
    question: str
    device_type: str = "generic"

@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not client.api_key:
        return {"answer": "Please set your OPENAI_API_KEY environment variable"}
    
    # Build device-specific system prompt
    system_msg = "You are a network engineer assistant. "
    
    if request.device_type.lower() == "cisco":
        system_msg += "Focus on Cisco IOS/IOS-XE commands and syntax. Provide specific 'show' and 'configure' commands. "
    elif request.device_type.lower() == "juniper":
        system_msg += "Focus on Junos commands and syntax. Use 'show' and 'set' command formats. "
    elif request.device_type.lower() == "arista":
        system_msg += "Focus on Arista EOS commands and syntax. Use EOS-specific features and commands. "
    elif request.device_type.lower() == "palo alto":
        system_msg += "Focus on Palo Alto firewall commands and web interface guidance. "
    else:
        system_msg += "Provide vendor-neutral network guidance. "
    
    system_msg += "Give concise, practical answers with specific commands when relevant."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": request.question}
            ],
            max_tokens=200
        )
        return {
            "answer": response.choices[0].message.content,
            "device_type": request.device_type
        }
    except Exception as e:
        return {"answer": f"AI service unavailable: {str(e)}"}

@app.get("/devices")
def supported_devices():
    return {
        "supported_devices": ["cisco", "juniper", "arista", "palo alto", "generic"],
        "usage": "Include device_type in your JSON request for device-specific help"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
