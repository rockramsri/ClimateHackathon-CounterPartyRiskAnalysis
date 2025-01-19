from transformers import pipeline # type: ignore

# Initialize a sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_citations(citations):
    """
    Analyzes the sentiment of each citation and calculates an overall semantic score.
    
    Args:
        citations (list of str): List of citation texts or paragraphs.
    
    Returns:
        dict: A dictionary containing detailed sentiment analysis results for each citation
              and an overall semantic score.
    """
    if not citations:
        return {"error": "No citations provided"}

    sentiment_results = []
    total_score = 0

    for citation in citations:
        # Analyze sentiment for the citation
        sentiment = sentiment_analyzer(citation)[0]
        sentiment_label = sentiment['label']
        sentiment_score = sentiment['score']
        
        # Map sentiment to a numeric score: Positive -> +1, Negative -> -1, Neutral -> 0
        if sentiment_label == "POSITIVE":
            numeric_score = sentiment_score
        elif sentiment_label == "NEGATIVE":
            numeric_score = -sentiment_score
        else:
            numeric_score = 0
        
        # Append results
        sentiment_results.append({
            "text": citation,
            "sentiment": sentiment_label,
            "confidence": sentiment_score,
            "numeric_score": numeric_score
        })
        
        # Accumulate the score
        total_score += numeric_score

    # Calculate overall semantic score
    overall_score = total_score / len(citations)

    return {
        "sentiment_results": sentiment_results,
        "overall_semantic_score": overall_score
    }

# Example usage
if __name__ == "__main__":
    citations = [
        "The company has been praised for its innovative solutions and rapid growth.",
        "However, recent reports have criticized its handling of employee relations.",
        "Investors remain optimistic about the company's long-term prospects."
    ]

    result = analyze_citations(citations)

    print("Sentiment Analysis Results:")
    for i, res in enumerate(result["sentiment_results"], start=1):
        print(f"Citation {i}:")
        print(f"  Text: {res['text']}")
        print(f"  Sentiment: {res['sentiment']} (Confidence: {res['confidence']:.2f})")
        print(f"  Numeric Score: {res['numeric_score']:.2f}")
    
    print(f"\nOverall Semantic Score: {result['overall_semantic_score']:.2f}")