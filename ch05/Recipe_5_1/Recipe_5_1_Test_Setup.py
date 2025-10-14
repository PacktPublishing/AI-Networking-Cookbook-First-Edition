from langchain_community.llms import Ollama
import requests

def test_docker_connection():
    """Test if Docker Ollama is accessible"""
    print("Testing Docker Ollama connection...")
    
    try:
        # Test direct API connection
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("Docker Ollama API is accessible")
        else:
            print("Docker Ollama API not responding")
            return False
            
        # Test LangChain connection
        llm = Ollama(
            model="llama2:7b-chat",
            base_url="http://localhost:11434"
        )
        
        ai_response = llm.invoke("What is OSPF in networking?")
        print("LangChain successfully connected to Docker Ollama")
        print(f"AI Response: {ai_response[:100]}...")
        return True
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_docker_connection():
        print("\n Ready for networking AI!")
    else:
        print("\n Check your Docker setup and try again.")