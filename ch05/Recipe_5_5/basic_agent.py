from langchain.agents import initialize_agent, AgentType
from langchain_ollama import OllamaLLM
from simple_tools import create_tools

class SimpleAgent:
    """Simple interactive network agent"""
    
    def __init__(self):
        self.llm = OllamaLLM(model="llama2:7b-chat", base_url="http://localhost:11434")
        self.tools = create_tools()
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=2,
            handle_parsing_errors=True  # ← This fixes the parsing error!
        )
    
    def analyze(self, config, question):
        """Analyze config with agent"""
        prompt = f"Config: {config}\nQuestion: {question}\nUse available tools to help answer."
        return self.agent.invoke(prompt)

if __name__ == "__main__":
    # Load config
    with open("mock_data/router_config.txt", 'r') as f:
        config = f.read()
    
    agent = SimpleAgent()
    
    print("Interactive Network Agent")
    print("Available tools: IP_Finder, Device_ID")
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("Ask about the config: ").strip()
        if question.lower() == 'quit':
            break
        
        try:
            result = agent.analyze(config, question)
            print(f"Agent: {result}\n")
        except Exception as e:
            print(f"Error: {e}\n")