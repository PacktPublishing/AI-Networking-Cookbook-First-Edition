import openai
import json
import os
import time

# Simple test questions for networking
TEST_QUESTIONS = [
    {
        "id": "ospf_config",
        "question": "Configure OSPF area 0 on a Cisco router",
        "category": "configuration"
    },
    {
        "id": "bgp_troubleshoot", 
        "question": "BGP neighbor stuck in Idle state. What to check?",
        "category": "troubleshooting"
    },
    {
        "id": "vlan_basic",
        "question": "Create VLAN 100 named Sales on a switch",
        "category": "configuration"
    }
]

def test_model(model_name):
    """Test a model with networking questions"""
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    results = []
    
    print(f"Testing {model_name}...")
    
    for question in TEST_QUESTIONS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": question["question"]}],
                max_tokens=150,
                temperature=0.1
            )
            
            results.append({
                "question_id": question["id"],
                "question": question["question"],
                "category": question["category"],
                "model": model_name,
                "response": response.choices[0].message.content
            })
            
            print(f"  ✓ {question['id']}")
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"  ✗ {question['id']}: {e}")
    
    return results

def main():
    # Test these three models
    models = ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"]
    all_results = []
    
    for model in models:
        results = test_model(model)
        all_results.extend(results)
    
    # Save results
    with open('model_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nDone! Saved {len(all_results)} responses to model_test_results.json")

if __name__ == "__main__":
    main()
    