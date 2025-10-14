#!/usr/bin/env python3
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Layer 1: Basic role and context
layer1 = """
You are a network engineer designing a simple branch office network.
"""

# Layer 2: Basic task definition
layer2 = """
Design a basic network configuration for a small branch office with 20 users.
The office needs internet connectivity and basic network services.
"""

# Layer 3: Technical requirements for reachability
layer3 = """
REQUIREMENTS:
- 1 router (Cisco ISR 4321)
- 1 switch (Cisco Catalyst 9200-24P)
- Internet connection via ISP
- Internal network: 192.168.10.0/24
- DHCP for user devices
- Basic routing configuration

Provide the complete configuration for both devices.
"""

# Build the complete prompt gradually
complete_prompt = f"{layer1}\n\n{layer2}\n\n{layer3}"

print("=== GRADUAL PROMPT BUILDING - BASIC REACHABILITY ===")
print("Complete prompt:")
print(complete_prompt)
print("\n" + "="*60 + "\n")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": complete_prompt}]
)

print("Generated Configuration:")
print(response.choices[0].message.content) 