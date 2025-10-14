from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

directed_prompt = """
You are a senior network engineer specializing in BGP routing protocols. 
I need you to generate a BGP configuration for a Cisco ASR9000 router that will:

1. Establish EBGP peering with two upstream ISPs (AS 65001 and AS 65002)
2. Implement route filtering to accept only default routes from upstreams
3. Set up load balancing between the two upstreams
4. Include basic security hardening for BGP sessions

My router's AS number is 65100, and the peer IPs are:
- ISP1 (AS 65001): 192.168.1.1
- ISP2 (AS 65002): 192.168.2.1

Provide the configuration in IOS-XR format with explanatory comments.
"""

response_directed = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": directed_prompt}]
)

print("Directed Response:")
print(response_directed.choices[0].message.content)
