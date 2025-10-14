import json
import openai
import os

def load_results():
    """Load test results from previous script"""
    with open('model_test_results.json', 'r') as f:
        return json.load(f)

def evaluate_response(result):
    """Use GPT-4o to score response quality"""
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""Rate this network engineering response 1-10:

Question: {result['question']}
Response: {result['response']}

Score based on accuracy and usefulness.
Format: SCORE: X - brief reason"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.1
        )
        
        eval_text = response.choices[0].message.content
        
        # Extract score
        if "SCORE:" in eval_text:
            score_part = eval_text.split("SCORE:")[1].split("-")[0].strip()
            score = float(score_part)
            explanation = eval_text.split("-", 1)[1].strip() if "-" in eval_text else ""
            return score, explanation
        return 5.0, "Could not parse score"
        
    except Exception as e:
        print(f"Error: {e}")
        return 5.0, "Evaluation failed"

def main():
    results = load_results()
    evaluations = []
    
    print("Evaluating responses...")
    
    for result in results:
        print(f"Evaluating {result['model']} - {result['question_id']}")
        score, explanation = evaluate_response(result)
        
        evaluations.append({
            "question_id": result["question_id"],
            "model": result["model"],
            "category": result["category"],
            "score": score,
            "explanation": explanation
        })
    
    # Save evaluations
    with open('response_evaluations.json', 'w') as f:
        json.dump(evaluations, f, indent=2)
    
    print(f"Done! Saved evaluations to response_evaluations.json")

if __name__ == "__main__":
    main()