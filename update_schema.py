from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def update_schema():
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["News"]
    collection = db["originalArticles"]
    
    # Update all documents to include new fields with default values
    result = collection.update_many(
        {
            # Find documents that don't have these fields
            "$or": [
                {"importance_score": {"$exists": False}},
                {"is_ranked": {"$exists": False}}
            ]
        },
        {
            # Set default values
            "$set": {
                "importance_score": 0,
                "is_ranked": 0
            }
        }
    )
    
    print(f"Modified {result.modified_count} documents to include ranking fields")
    
    # Verify the schema update
    total_docs = collection.count_documents({})
    docs_with_importance = collection.count_documents({"importance_score": {"$exists": True}})
    docs_with_ranked = collection.count_documents({"is_ranked": {"$exists": True}})
    
    print(f"\nSchema verification:")
    print(f"Total documents: {total_docs}")
    print(f"Documents with importance_score: {docs_with_importance}")
    print(f"Documents with is_ranked: {docs_with_ranked}")

if __name__ == "__main__":
    update_schema() 