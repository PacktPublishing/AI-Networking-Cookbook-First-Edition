#!/usr/bin/env python3
"""
Simple script to generate a fat-tree topology dot file using OpenAI
"""

import openai
import os

# Setup OpenAI
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Generate dot file content
prompt = """Generate a Graphviz DOT file for a fat-tree network topology:
- 2 Core routers: core1, core2
- 4 Spine routers: spine1, spine2, spine3, spine4  
- 8 Leaf routers: leaf1, leaf2, leaf3, leaf4, leaf5, leaf6, leaf7, leaf8

Each core connects to all spines, each spine connects to all leaves.
Use different colors for each router type. Return only the DOT file content."""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

# Extract and save dot file content
content = response.choices[0].message.content

# Find the actual DOT content (between graph/digraph and the closing brace)
import re
dot_match = re.search(r'((?:di)?graph\s+\w*\s*\{.*\})', content, re.DOTALL)

if dot_match:
    dot_content = dot_match.group(1)
else:
    # Fallback: try to clean up the content
    lines = content.split('\n')
    dot_lines = []
    in_graph = False
    for line in lines:
        if 'graph' in line and '{' in line:
            in_graph = True
        if in_graph:
            dot_lines.append(line)
        if in_graph and '}' in line:
            break
    dot_content = '\n'.join(dot_lines)

with open("fat_tree_topology.dot", "w") as f:
    f.write(dot_content)

print("Generated fat_tree_topology.dot")