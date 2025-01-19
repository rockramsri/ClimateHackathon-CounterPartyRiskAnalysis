from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
import logging
from juriscraper.opinions.united_states.federal_appellate import ca1
import pandas as pd
from transformers import pipeline

# Initialize FastAPI and logging
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Load credit score data
df = pd.read_csv("Rating_with_history.csv")
aggregated = pd.read_csv("Rating_without_history.csv")


# Helper Functions
def get_company_lawsuits(company_name: str) -> List[Dict[str, Any]]:
    """
    Fetch lawsuits related to the company using Juriscraper.
    """
    try:
        site = ca1.Site()
        site.parse()

        lawsuits = []
        for opinion in site:
            if company_name.lower() in str(opinion).lower():
                lawsuit_details = {
                    'case_name': opinion.case_name,
                    'date_filed': opinion.date_filed,
                    'docket_number': opinion.docket,
                    'neutral_citation': opinion.neutral_citation,
                    'summary': opinion.summary,
                    'url': opinion.url if hasattr(opinion, 'url') else None
                }
                lawsuits.append(lawsuit_details)
        return lawsuits
    except Exception as e:
        logger.error(f"Error fetching lawsuits: {e}")
        return {"error": str(e)}


def get_current_credit_category(company_name: str) -> str:
    """
    Get the current credit category for a company.
    """
    result = aggregated.loc[aggregated['Name'] == company_name, 'Average_Rating']
    return str(result.iloc[0]) if not result.empty else "Medium Risk"


def get_ratings_by_company(company_name: str) -> Dict[str, Any]:
    """
    Get the credit rating history of a company.
    """
    result = df.loc[df['Name'] == company_name]
    if not result.empty:
        return result.set_index('Date')['Rating'].to_dict()
    return {"error": "Company not found"}


def summarize_text(content: str) -> str:
    """
    Summarize text content using a summarization model.
    """
    try:
        summary = summarizer(content, max_length=50, min_length=10, do_sample=False)[0]['summary_text']
        return summary
    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        return "Error summarizing text"
    
# Function 1: Fetch News Articles
def fetch_news_articles(company_name: str, api_key: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches news articles based on the company name using NewsAPI.
    """
    url = f"https://newsapi.org/v2/everything"
    params = {
        "q": company_name,
        "sortBy": "relevancy",
        "pageSize": max_results,
        "apiKey": api_key
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return articles
    else:
        raise Exception(f"Error fetching news articles: {response.status_code}, {response.text}")


# FastAPI Endpoints
@app.get("/legal-cases")
async def retrieve_legal_cases(company: str):
    """
    Retrieve legal cases for a given company.
    """
    try:
        lawsuits = get_company_lawsuits(company)
        if "error" in lawsuits:
            raise Exception(lawsuits["error"])
        return {"status": "success", "cases": lawsuits}
    except Exception as e:
        logger.error(f"Error in /legal-cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/credit-score")
async def retrieve_credit_score(company: str):
    """
    Retrieve the current credit score for a company.
    """
    try:
        credit_score = get_current_credit_category(company)
        return {"status": "success", "current_credit_score": credit_score}
    except Exception as e:
        logger.error(f"Error in /credit-score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/credit-history")
async def retrieve_credit_history(company: str):
    """
    Retrieve the credit rating history for a company.
    """
    try:
        credit_history = get_ratings_by_company(company)
        if "error" in credit_history:
            raise Exception(credit_history["error"])
        return {"status": "success", "credit_history": credit_history}
    except Exception as e:
        logger.error(f"Error in /credit-history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/summarize")
async def summarize_paragraph(content: str):
    """
    Summarize a given paragraph.
    """
    try:
        summary = summarize_text(content)
        return {"status": "success", "summary": summary}
    except Exception as e:
        logger.error(f"Error in /summarize: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Function 1: Fetch News Articles
def fetch_news_articles(company_name: str, api_key: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches news articles based on the company name using NewsAPI.
    """
    url = f"https://newsapi.org/v2/everything"
    params = {
        "q": company_name,
        "sortBy": "relevancy",
        "pageSize": max_results,
        "apiKey": api_key
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return articles
    else:
        raise Exception(f"Error fetching news articles: {response.status_code}, {response.text}")

# Function 2: Summarize Articles and Extract Citations
def summarize_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Summarizes articles and extracts citations and reference links.
    """
    summaries = []
    for article in articles:
        content = article.get("content") or article.get("description", "")
        if not content:
            continue

        # Summarize the content
        try:
            summary = summarizer(content, max_length=50, min_length=10, do_sample=False)[0]['summary_text']
        except Exception:
            summary = "Error summarizing article."
        
        # Extract citation and reference link
        citation = {
            "summary": summary,
            "source": article.get("source", {}).get("name", "Unknown"),
            "url": article.get("url", "No URL Provided")
        }
        summaries.append(citation)
    return summaries

# Function 3: Calculate Semantic Score
def calculate_semantic_score(citations: List[Dict[str, Any]]) -> float:
    """
    Calculates an overall semantic score based on the quality and number of citations.
    """
    if not citations:
        return 0.0  # No citations, score is 0
    
    # Example scoring mechanism: Use the number of citations and the presence of valid URLs
    score = sum(10 if citation["url"] != "No URL Provided" else 5 for citation in citations)
    return score / len(citations)  # Normalize score

# FastAPI Endpoint for News
@app.get("/news")
async def retrieve_news(company: str):
    """
    Fetch news articles, summarize them, and calculate semantic score for a given company.
    """
    api_key = "YOUR_NEWSAPI_KEY"  # Replace with your NewsAPI key
    try:
        # Fetch news articles
        articles = fetch_news_articles(company, api_key)
        if not articles:
            return {"status": "error", "message": "No news articles found."}
        
        # Summarize articles and extract citations
        citations = summarize_articles(articles)
        
        # Calculate semantic score
        semantic_score = calculate_semantic_score(citations)
        
        return {
            "status": "success",
            "citations": citations,
            "semantic_score": semantic_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI service!"}