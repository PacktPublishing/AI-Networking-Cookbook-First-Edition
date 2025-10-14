from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

def create_security_template():
    """Template for security analysis"""
    
    template = """
You are a network security expert analyzing a configuration.

CONFIGURATION:
{config}

SECURITY ANALYSIS:
Please identify:
1. High-risk security issues
2. Medium-risk concerns  
3. Best practice recommendations

Rate each issue as HIGH, MEDIUM, or LOW risk.
Be specific about what needs to be fixed.

ANALYSIS:
"""
    
    return PromptTemplate(
        template=template,
        input_variables=["config"]
    )

def create_basic_overview_template():
    """Template for basic config overview"""
    
    template = """
You are a senior network engineer reviewing this configuration.

DEVICE CONFIG:
{config}

OVERVIEW REQUEST:
Provide a brief overview including:
1. Device type and purpose
2. Key configuration highlights
3. One potential improvement

Keep it concise and practical.

OVERVIEW:
"""
    
    return PromptTemplate(
        template=template,
        input_variables=["config"]
    )

def test_templates():
    """Test the templates"""
    
    # Connect to Docker Ollama
    llm = Ollama(
        model="llama2:7b-chat",
        base_url="http://localhost:11434"
    )
    
    # Load a test config
    with open("mock_data/security_issue.txt", 'r') as f:
        config = f.read()
    
    # Test security template
    print("Testing Security Template")
    print("=" * 40)
    
    security_template = create_security_template()
    security_prompt = security_template.format(config=config)
    security_result = llm.invoke(security_prompt)
    
    print(security_result)
    print("\n" + "=" * 40)
    
    # Test overview template
    print("Testing Overview Template")
    print("=" * 40)
    
    overview_template = create_basic_overview_template()
    overview_prompt = overview_template.format(config=config)
    overview_result = llm.invoke(overview_prompt)
    
    print(overview_result)

if __name__ == "__main__":
    test_templates()
