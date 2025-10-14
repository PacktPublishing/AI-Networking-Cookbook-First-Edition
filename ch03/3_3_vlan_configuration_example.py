#!/usr/bin/env python3
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Task description
task_description = """
Generate VLAN configurations following our corporate standards.
Each VLAN should have proper naming, description, and associated services.

Here are examples of the correct format and style:

Example 1:
Input: VLAN for user workstations, ID 100, subnet 10.100.0.0/24
Output: 
vlan 100
 name USERS_WORKSTATION
 state active
!
interface Vlan100
 description User Workstations - Building A
 ip address 10.100.0.1 255.255.255.0
 ip helper-address 10.10.10.100
 no ip redirects
 no ip proxy-arp

Example 2:
Input: VLAN for guest WiFi, ID 200, subnet 192.168.200.0/24
Output:
vlan 200
 name GUEST_WIFI
 state active
!
interface Vlan200
 description Guest WiFi Network
 ip address 192.168.200.1 255.255.255.0
 ip helper-address 10.10.10.100
 ip access-group GUEST_FILTER in
 no ip redirects
 no ip proxy-arp

Now, apply the same format and style to this input:
VLAN for IP cameras, ID 150, subnet 10.150.0.0/24
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": task_description}]
)

print("Generated VLAN Configuration:")
print(response.choices[0].message.content) 