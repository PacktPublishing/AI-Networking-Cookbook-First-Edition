#!/usr/bin/env python3
"""
VLAN MOP Generator using OpenAI API
Generates Method of Procedure documents for Cisco IOS VLAN configuration
"""

import openai
import os
import sys
from datetime import datetime

class VLANMOPGenerator:
    def __init__(self, api_key):
        """Initialize the MOP generator with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
        
    def generate_mop(self, vlan_config):
        """Generate a MOP for VLAN configuration"""
        
        prompt = f"""
Generate a Method of Procedure (MOP) document for configuring VLANs on a Cisco IOS device:

Device: {vlan_config.get('device_name', 'Cisco Switch')}
VLANs: {vlan_config.get('vlans', [])}
Trunk ports: {vlan_config.get('trunk_ports', [])}
Access ports: {vlan_config.get('access_ports', {})}

Include: prerequisites, configuration commands, verification steps, and rollback procedures.
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a network engineer. Generate professional MOP documents for Cisco IOS VLAN configuration."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content

def main():
    # VLAN configuration
    vlan_config = {
        "device_name": "SW-CORE-01",
        "vlans": [
            {"id": 10, "name": "USERS"},
            {"id": 20, "name": "SERVERS"},
            {"id": 30, "name": "GUEST"}
        ],
        "trunk_ports": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"],
        "access_ports": {
            "GigabitEthernet1/0/10": {"vlan": 10},
            "GigabitEthernet1/0/11": {"vlan": 20},
            "GigabitEthernet1/0/12": {"vlan": 30}
        }
    }
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set!")
        sys.exit(1)
    
    # Generate and save MOP
    generator = VLANMOPGenerator(api_key)
    mop_document = generator.generate_mop(vlan_config)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"VLAN_MOP_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(mop_document)
    
    print(f"MOP saved to: {filename}")

if __name__ == "__main__":
    main()