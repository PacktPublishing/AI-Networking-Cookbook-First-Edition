#!/usr/bin/env python3
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Task description
task_description = """
Generate interface descriptions following our corporate naming standard.
The descriptions should be informative but concise, following a specific format.

Here are examples of the correct format and style:

Example 1:
Input: GigabitEthernet0/1 connected to SW-DIST-01 port Gi0/5
Output: interface GigabitEthernet0/1
 description UPLINK_TO_SW-DIST-01_Gi0/5_10GB_CORE

Example 2: 
Input: GigabitEthernet0/2 connected to user workstation in room 205
Output: interface GigabitEthernet0/2
 description ACCESS_ROOM205_WORKSTATION_1GB_USER

Example 3:
Input: TenGigabitEthernet0/1 connected to firewall outside interface
Output: interface TenGigabitEthernet0/1
 description FIREWALL_OUTSIDE_PA3220_10GB_SECURITY

Now, apply the same format and style to this input:
GigabitEthernet0/3 connected to IP phone in conference room B
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": task_description}]
)

print("Generated Interface Description:")
print(response.choices[0].message.content) 