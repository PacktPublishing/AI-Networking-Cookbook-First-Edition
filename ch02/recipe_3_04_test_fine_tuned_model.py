# script4_test_fine_tuned_model.py
import os
from openai import OpenAI

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

with open('fine_tuned_model_id.txt', 'r') as f:
    fine_tuned_model = f.read().strip()

query = "Configure BGP for AS 65001 with neighbor 192.168.1.2 in AS 65002"

response = client.chat.completions.create(
    model=fine_tuned_model,
    messages=[
        {"role": "system", "content": "You are a network engineer. Generate BGP configuration."},
        {"role": "user", "content": query}
    ],
    max_tokens=200,
    temperature=0.1
)

print("FINE-TUNED MODEL OUTPUT:")
print(response.choices[0].message.content)