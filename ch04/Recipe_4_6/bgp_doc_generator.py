#!/usr/bin/env python3
"""
Simple BGP Documentation Generator
"""

import subprocess

def generate_bgp_documentation():
    """Generate BGP documentation from configuration file"""
    
    # Read BGP configuration
    with open("configs/bgp-config.txt", 'r') as f:
        config = f.read()
    
    # Create prompt for LLM
    prompt = f"""Analyze this BGP configuration:

{config}

Provide:
1. AS number and Router ID
2. BGP neighbors and their AS numbers  
3. Networks being advertised

Keep it simple and clear."""

    # Query the LLM
    result = subprocess.run([
        'docker', 'exec', 'ch04_ollama_1',
        'ollama', 'run', 'codellama:7b', prompt
    ], capture_output=True, text=True)
    
    # Create documentation
    doc_content = f"""# BGP Configuration Documentation

## Analysis
{result.stdout}

## Configuration
"""
    
    # Save documentation
    with open("bgp_documentation.md", 'w') as f:
        f.write(doc_content)
    
    print("BGP documentation saved: bgp_documentation.md")

if __name__ == "__main__":
    generate_bgp_documentation()