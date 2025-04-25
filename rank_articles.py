import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from pprint import pprint
import json
from datetime import datetime

load_dotenv()

def get_article_rank(article, client):
    """Rank an article using GPT-4 based on relevance and importance"""
    prompt = f"""Please analyze this news article and provide a ranking score from 1-10 based on:
    1. Relevance to current events
    2. Importance to general audience
    3. Impact and significance
    4. Timeliness
    
    Article Title: {article.get('title', 'No Title')}
    Summary: {article.get('summary', 'No Summary')}
    Published: {article.get('publishedAt', 'No Date')}
    Source: {article.get('source', {}).get('name', 'Unknown')}
    Category: {article.get('custom_category', 'Uncategorized')}
    
    Provide your response in JSON format with the following structure:
    {{
        "score": <number between 1-10>,
        "reasoning": "<brief explanation of the score>"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a news article ranking expert. Analyze articles and provide scores based on relevance and importance. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Get the response content
        content = response.choices[0].message.content
        
        # Remove markdown code block markers and clean up the string
        content = content.replace("```json", "").replace("```", "").strip()
        
        # Parse the JSON
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Cleaned content:", repr(content))
            return {"score": 5, "reasoning": "Error parsing response"}
            
    except Exception as e:
        print(f"Error ranking article: {e}")
        return {"score": 5, "reasoning": "Error in ranking process"}

def rank_articles_by_category():
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_CHATGPT_APIKEY"),
        api_version="2024-02-15-preview",
        azure_endpoint=os.getenv("AZURE_CHATGPT_ENDPOINT")
    )
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI")
    client_mongo = MongoClient(mongo_uri)
    db = client_mongo["News"]
    collection = db["originalArticles"]
    
    # Get all categories
    categories = ["Trending", "Business", "Tech&AI", "Entertainment", "Sports", "USA", "India"]
    
    for category in categories:
        print(f"\nProcessing category: {category}")
        print("=" * 50)
        
        # Get articles for this category
        query = {
            "custom_category": category,
            "is_summarized": 1
        }
        articles = list(collection.find(query).sort("publishedAt", -1))
        
        print(f"Found {len(articles)} articles to rank")
        
        # Rank each article
        for i, article in enumerate(articles):
            print(f"\nRanking article {i+1}/{len(articles)}")
            print(f"Title: {article.get('title', 'No Title')}")
            
            # Get ranking
            ranking = get_article_rank(article, client)
            print(f"Score: {ranking['score']}")
            print(f"Reasoning: {ranking['reasoning']}")
            
            # Update MongoDB with ranking
            collection.update_one(
                {"_id": article["_id"]},
                {
                    "$set": {
                        "ranking_score": ranking["score"],
                        "ranking_reasoning": ranking["reasoning"],
                        "last_ranked": datetime.utcnow(),
                        "is_ranked": 1  # Add this flag to indicate the article has been ranked
                    }
                }
            )
            print("Updated in database")
            print("-" * 50)

if __name__ == "__main__":
    rank_articles_by_category() 