#!/usr/bin/env python3
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simple base scenario
base_scenario = """
I have a network with the following devices:
- 2 core switches (Cisco Catalyst 9400)
- 4 distribution switches (Cisco Catalyst 9300)
- 8 access switches (Cisco Catalyst 9200)

Create an inventory document for this network.
"""

# Request YAML format
yaml_prompt = base_scenario + """

Return the inventory in YAML format suitable for Ansible inventory.
Structure it as:
- Group devices by role using YAML groups
- Include vars for each group (os_type, default_credentials, etc.)
- Add individual host variables where needed
- Make it ready to use with ansible-playbook commands

Provide ONLY the YAML output, no additional text.
"""

response_yaml = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": yaml_prompt}]
)

print("YAML Format Response:")
print(response_yaml.choices[0].message.content) 
