from langchain_community.llms import Ollama

def load_config(filename):
    """Load a mock configuration file"""
    with open(f"mock_data/{filename}", 'r') as f:
        return f.read()

def analyze_config(config_text, config_name):
    """Analyze network config using Docker Ollama"""
    llm = Ollama(
        model="llama2:7b-chat",
        base_url="http://localhost:11434"
    )
    
    prompt = f"""
Analyze this network configuration:

{config_text}

Please tell me:
1. What type of device is this (router/switch/firewall)?
2. What is its main function?
3. Any obvious issues or concerns?

Keep your response clear and practical for a network engineer.
"""
    
    return llm.invoke(prompt)

def main():
    """Analyze all mock configurations"""
    configs = [
        "router_config.txt",
        "switch_config.txt", 
        "problem_config.txt"
    ]
    
    print("AI Analysis of Mock Network Configurations")
    print("=" * 50)
    
    for config_file in configs:
        print(f"\n Analyzing {config_file}")
        print("-" * 30)
        
        config_text = load_config(config_file)
        analysis = analyze_config(config_text, config_file)
        print(analysis)
        
        # Save results
        output_file = f"outputs/{config_file.replace('.txt', '_analysis.txt')}"
        with open(output_file, 'w') as f:
            f.write(f"Analysis of {config_file}\n")
            f.write("=" * 30 + "\n")
            f.write(analysis)
        print(f"💾 Saved analysis to {output_file}")


if __name__ == "__main__":
    main()
