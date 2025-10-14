#!/usr/bin/env python3
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Layer 1: Basic role and context
layer1 = """
You are a network engineer designing a complete enterprise-grade branch office network.
"""

# Layer 2: Basic task definition
layer2 = """
Design a comprehensive network configuration for a small branch office with 20 users.
The office needs internet connectivity, security, and monitoring capabilities.
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

# Layer 4: Security requirements
layer4 = """
SECURITY REQUIREMENTS:
- Access Control Lists (ACLs) to block unwanted traffic
- Enable SSH for remote management, disable Telnet
- Configure strong passwords and enable secret
- Block access to social media sites (Facebook, Twitter)
- Allow only necessary ports outbound (HTTP, HTTPS, DNS)
- Secure SNMP community strings
"""

# Layer 5: Monitoring requirements (NEW)
layer5 = """
MONITORING REQUIREMENTS:
- Enable SNMP for network monitoring
- Configure syslog to send logs to 192.168.10.100
- Set up NetFlow on the router for traffic analysis
- Enable interface monitoring and alerting
- Configure NTP for accurate timestamps (pool.ntp.org)
- Add CDP/LLDP for network discovery
- Enable device health monitoring (CPU, memory, temperature)

Include all monitoring configurations and ensure proper logging setup.
"""

# Build the complete prompt gradually
complete_prompt = f"{layer1}\n\n{layer2}\n\n{layer3}\n\n{layer4}\n\n{layer5}"

print("=== GRADUAL PROMPT BUILDING - ADDING MONITORING ===")
print("Complete prompt:")
print(complete_prompt)
print("\n" + "="*60 + "\n")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": complete_prompt}]
)

print("Generated Configuration:")
print(response.choices[0].message.content) 