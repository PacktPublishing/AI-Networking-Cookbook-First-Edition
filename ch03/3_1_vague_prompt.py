from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Bad example - vague and directionless
vague_prompt = "Help me with BGP configuration"

response_vague = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": vague_prompt}]
)

print("Vague Response:")
print(response_vague.choices[0].message.content)
print("\n" + "="*50 + "\n")