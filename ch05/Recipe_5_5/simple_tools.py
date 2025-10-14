from langchain.tools import Tool
import re

def find_ip_addresses(config_text):
    """Find IP addresses in config"""
    ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', config_text)
    return f"Found IP addresses: {', '.join(set(ips))}" if ips else "No IPs found"

def identify_device(config_text):
    """Identify device type"""
    if "switchport" in config_text.lower():
        return "Device type: Switch"
    elif "router" in config_text.lower():
        return "Device type: Router"
    else:
        return "Device type: Unknown network device"

def create_tools():
    """Create simple tools for the agent"""
    return [
        Tool(name="IP_Finder", description="Find IP addresses in config", func=find_ip_addresses),
        Tool(name="Device_ID", description="Identify device type", func=identify_device)
    ]

if __name__ == "__main__":
    # Test tools directly
    with open("mock_data/router_config.txt", 'r') as f:
        config = f.read()
    
    tools = create_tools()
    for tool in tools:
        print(f"{tool.name}: {tool.func(config)}")