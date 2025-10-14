import json

def load_evaluations():
    """Load evaluation results"""
    with open('response_evaluations.json', 'r') as f:
        return json.load(f)

def analyze_results(evaluations):
    """Analyze model performance"""
    print("MODEL PERFORMANCE ANALYSIS")
    print("=" * 40)
    
    # Group scores by model
    model_scores = {}
    for eval in evaluations:
        model = eval['model']
        if model not in model_scores:
            model_scores[model] = []
        model_scores[model].append(eval['score'])
    
    # Calculate averages
    print("\nOVERALL SCORES:")
    results = []
    for model, scores in model_scores.items():
        avg_score = sum(scores) / len(scores)
        results.append((model, avg_score))
        print(f"{model:<15} Average: {avg_score:.1f}/10")
    
    # Sort by performance
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Performance by category
    print(f"\nBY CATEGORY:")
    categories = {}
    for eval in evaluations:
        cat = eval['category']
        model = eval['model']
        if cat not in categories:
            categories[cat] = {}
        if model not in categories[cat]:
            categories[cat][model] = []
        categories[cat][model].append(eval['score'])
    
    for category, models in categories.items():
        print(f"\n{category.title()}:")
        for model, scores in models.items():
            avg = sum(scores) / len(scores)
            print(f"  {model}: {avg:.1f}")
    
    # Recommendation
    best_model = results[0][0]
    best_score = results[0][1]
    
    print(f"\nRECOMMENDATION:")
    print(f"{best_model} performs best with {best_score:.1f}/10")
    
    # Cost consideration
    costs = {
        'gpt-3.5-turbo': 0.002,
        'gpt-4o-mini': 0.015,  
        'gpt-4o': 0.06
    }
    
    print(f"\nCOST vs PERFORMANCE:")
    for model, score in results:
        if model in costs:
            cost = costs[model]
            value = score / (cost * 1000)
            print(f"{model}: Score {score:.1f} | ${cost:.3f}/1k tokens | Value: {value:.0f}")
    
    return results[0][0]  # Return best model

def main():
    evaluations = load_evaluations()
    best_model = analyze_results(evaluations)
    
    # Save simple summary
    summary = {"best_model": best_model}
    with open('model_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSummary saved to model_summary.json")

if __name__ == "__main__":
    main()
