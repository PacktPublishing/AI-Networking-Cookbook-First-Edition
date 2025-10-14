#!/usr/bin/env python3
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initial request
print("=== ITERATION 1: Initial Request ===")
initial_prompt = """
Create a basic access control list (ACL) for our office network.
We need to control traffic between our internal network and the internet.
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": initial_prompt}]
)

response1 = response.choices[0].message.content
print("Response:")
print(response1)
print("\n" + "="*60 + "\n")

# Provide feedback for improvement
print("=== ITERATION 2: After Feedback ===")
feedback = """
The previous ACL is too basic. Please improve it with these requirements:

1. Our internal network is 192.168.1.0/24
2. Allow web traffic (HTTP/HTTPS) outbound
3. Allow DNS queries to 8.8.8.8
4. Block all social media sites
5. Deny everything else explicitly

Please create a more specific ACL addressing these requirements.
"""

# Continue the conversation with feedback
conversation = [
    {"role": "user", "content": initial_prompt},
    {"role": "assistant", "content": response1},
    {"role": "user", "content": feedback}
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=conversation
)

response2 = response.choices[0].message.content
print("Feedback provided:")
print(feedback)
print("\nImproved response:")
print(response2) 