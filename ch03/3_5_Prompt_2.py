#!/usr/bin/env python3
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Layer 1: Basic role and context
layer1 = """
You are a network engineer designing a secure branch office network.
"""

# Layer 2: Basic task definition  
layer2 = """
Design a network configuration for a small branch office with 20 users.
The office needs internet connectivity and basic network services.
"""

# Layer 3: Technical requirements for reachability
layer3 = """
BASIC REQUIREMENTS:
- 1 router (Cisco ISR 4321)
- 1 switch (Cisco Catalyst 9200-24P)
- Internet connection via ISP
- Internal network: 192.168.10.0/24
- DHCP for user devices
- Basic routing configuration
"""

# Layer 4: Security requirements (NEW)
layer4 = """
SECURITY REQUIREMENTS:
- Access Control Lists (ACLs) to block unwanted traffic
- Enable SSH for remote management, disable Telnet
- Configure strong passwords and enable secret
- Block access to social media sites (Facebook, Twitter)
- Allow only necessary ports outbound (HTTP, HTTPS, DNS)
- Secure SNMP community strings

Include all security configurations in the device setup.
"""

# Build the complete prompt gradually
complete_prompt = f"{layer1}\n\n{layer2}\n\n{layer3}\n\n{layer4}"

print("=== GRADUAL PROMPT BUILDING - ADDING SECURITY ===")
print("Complete prompt:")
print(complete_prompt)
print("\n" + "="*60 + "\n")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": complete_prompt}]
)

print("Generated Configuration:")
print(response.choices[0].message.content) 