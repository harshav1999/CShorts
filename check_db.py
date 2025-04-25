from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

def check_database():
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["News"]
    collection = db["originalArticles"]
    
    # Get total count of documents
    total_docs = collection.count_documents({})
    print(f"\nTotal documents in database: {total_docs}")
    
    # Check documents by category
    categories = ["Trending", "Business", "Tech&AI", "Entertainment", "Sports", "USA", "India"]
    print("\nDocuments by category:")
    for category in categories:
        count = collection.count_documents({"custom_category": category})
        print(f"{category}: {count} documents")
    
    # Check summarization status
    summarized = collection.count_documents({"is_summarized": 1})
    not_summarized = collection.count_documents({"is_summarized": 0})
    print(f"\nSummarization status:")
    print(f"Summarized: {summarized}")
    print(f"Not summarized: {not_summarized}")
    
    # Check ranking status
    ranked = collection.count_documents({"is_ranked": 1})
    not_ranked = collection.count_documents({"is_ranked": 0})
    print(f"\nRanking status:")
    print(f"Ranked: {ranked}")
    print(f"Not ranked: {not_ranked}")
    
    # Check for documents with importance scores
    with_scores = collection.count_documents({"importance_score": {"$gt": 0}})
    print(f"\nDocuments with importance scores > 0: {with_scores}")
    
    # Sample a few documents to verify structure
    print("\nSample document structure:")
    sample = collection.find_one({"is_summarized": 1, "is_ranked": 1})
    if sample:
        print("\nFields in sample document:")
        for field in sample.keys():
            print(f"- {field}")
        
        print("\nSample document content:")
        pprint({
            "title": sample.get("title"),
            "custom_category": sample.get("custom_category"),
            "is_summarized": sample.get("is_summarized"),
            "is_ranked": sample.get("is_ranked"),
            "importance_score": sample.get("importance_score"),
            "summary": sample.get("summary")[:100] + "..." if sample.get("summary") else None
        })

if __name__ == "__main__":
    check_database() 