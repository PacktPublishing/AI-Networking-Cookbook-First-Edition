from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
import os

def create_mixed_analysis_chain():
    """Chain using both local Ollama and OpenAI models with modern LCEL patterns"""
    
    # Local model for basic analysis (private, fast, free)
    local_llm = OllamaLLM(
        model="llama2:7b-chat",
        base_url="http://localhost:11434"
    )
    
    # OpenAI model for complex reasoning (powerful, costs money)
    openai_llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Step 1: Basic analysis with local model
    basic_analysis_template = PromptTemplate(
        input_variables=["config"],
        template="""
Analyze this network configuration and extract key facts:

{config}

Provide:
1. Device type and hostname
2. Interface summary
3. Protocols in use
4. Basic security observations

Keep it factual and concise.

BASIC ANALYSIS:
"""
    )
    
    # Step 2: Advanced reasoning with OpenAI
    advanced_analysis_template = PromptTemplate(
        input_variables=["config", "basic_analysis"],
        template="""
You are a senior network architect. Based on this basic analysis and configuration, provide strategic recommendations:

BASIC ANALYSIS:
{basic_analysis}

ORIGINAL CONFIG:
{config}

Provide advanced analysis:
1. Architecture assessment and design patterns
2. Security risk analysis with business impact
3. Performance optimization strategies
4. Scalability and future-proofing recommendations
5. Compliance and governance considerations

ADVANCED ANALYSIS:
"""
    )
    
    # Step 3: Combined synthesis with OpenAI
    synthesis_template = PromptTemplate(
        input_variables=["config", "basic_analysis", "advanced_analysis"],
        template="""
You are a Chief Technology Officer creating a comprehensive network assessment report. 
Synthesize the technical findings and strategic recommendations into actionable insights:

TECHNICAL FINDINGS:
{basic_analysis}

STRATEGIC RECOMMENDATIONS:
{advanced_analysis}

ORIGINAL CONFIGURATION:
{config}

Create a COMBINED EXECUTIVE SUMMARY that includes:

1. **Current State Assessment**: Merge technical facts with strategic context
2. **Priority Action Items**: Top 3 immediate actions needed (with timeline)
3. **Risk Matrix**: Critical/High/Medium risks with mitigation strategies  
4. **Investment Roadmap**: Short-term (0-6 months) vs Long-term (6+ months) recommendations
5. **Success Metrics**: KPIs to measure improvement

Format as an executive briefing suitable for C-level decision makers.

EXECUTIVE SUMMARY:
"""
    )
    
    # Create the basic analysis chain using LCEL
    basic_chain = basic_analysis_template | local_llm
    
    # Function to prepare input for advanced analysis
    def prepare_advanced_input(input_dict):
        """Prepare input for the advanced analysis chain"""
        return {
            "config": input_dict["config"],
            "basic_analysis": input_dict["basic_analysis"]
        }
    
    # Function to prepare input for synthesis
    def prepare_synthesis_input(input_dict):
        """Prepare input for the synthesis chain"""
        advanced_content = input_dict["advanced_analysis"]
        if hasattr(advanced_content, 'content'):
            advanced_text = advanced_content.content
        else:
            advanced_text = str(advanced_content)
            
        return {
            "config": input_dict["config"],
            "basic_analysis": input_dict["basic_analysis"],
            "advanced_analysis": advanced_text
        }
    
    # Create the advanced analysis chain using LCEL
    advanced_chain = advanced_analysis_template | openai_llm
    
    # Create the synthesis chain using LCEL
    synthesis_chain = synthesis_template | openai_llm
    
    # Create the complete mixed chain using LCEL
    mixed_chain = (
        RunnablePassthrough.assign(
            basic_analysis=basic_chain
        )
        | RunnablePassthrough.assign(
            advanced_analysis=RunnableLambda(prepare_advanced_input) | advanced_chain
        )
        | RunnablePassthrough.assign(
            combined_analysis=RunnableLambda(prepare_synthesis_input) | synthesis_chain
        )
    )
    
    return mixed_chain

# Test the mixed chain
def test_mixed_models():
    """Test chain with both local and OpenAI models"""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        return
    
    # Load test config
    test_config = """
hostname CoreRouter-HQ
interface GigabitEthernet0/0
 description Internet Connection
 ip address 203.0.113.1 255.255.255.252
interface GigabitEthernet0/1
 description LAN Connection
 ip address 10.0.1.1 255.255.255.0
router ospf 1
 network 10.0.1.0 0.0.0.255 area 0
access-list 100 permit tcp 10.0.1.0 0.0.0.255 any eq 80
access-list 100 permit tcp 10.0.1.0 0.0.0.255 any eq 443
access-list 100 deny ip any any log
"""
    
    print(" Testing Mixed Model Chain (Local + OpenAI + Synthesis)")
    print("=" * 70)
    
    try:
        chain = create_mixed_analysis_chain()
        results = chain.invoke({"config": test_config})
        
        print("\n LOCAL MODEL ANALYSIS:")
        print("-" * 30)
        print(results["basic_analysis"])
        
        print("\n OPENAI ADVANCED ANALYSIS:")
        print("-" * 30)
        # Extract content from ChatOpenAI response object
        advanced_content = results["advanced_analysis"]
        if hasattr(advanced_content, 'content'):
            print(advanced_content.content)
        else:
            print(advanced_content)
            
        print("\n COMBINED EXECUTIVE SUMMARY:")
        print("-" * 30)
        # Extract content from synthesis response
        combined_content = results["combined_analysis"]
        if hasattr(combined_content, 'content'):
            print(combined_content.content)
        else:
            print(combined_content)
        
    except Exception as e:
        print(f" Mixed chain failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mixed_models()