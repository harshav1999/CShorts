import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# === Load environment variables ===
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# === Step 1: Load your JSON data ===
with open("news_articles_with_full_content.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Ensure it's a list of documents
if isinstance(data, dict):
    data = [data]  # wrap single object in list

# === Step 2: Connect to MongoDB Atlas ===
client = MongoClient(mongo_uri)
db = client["News"]
collection = db["originalArticles"]

# === Step 3: Add is_summarized and check for duplicates ===
new_docs = []
for doc in data:
    title = doc.get("title")
    if not title:
        continue  # Skip if no title

    # Check if a document with the same title exists
    if collection.find_one({"title": title}):
        print(f"⏩ Skipped duplicate: {title}")
        continue

    doc["is_summarized"] = 0
    new_docs.append(doc)

# === Step 4: Insert only new documents ===
if new_docs:
    collection.insert_many(new_docs)
    print(f"✅ Inserted {len(new_docs)} new documents with is_summarized=0")
else:
    print("⚠️ No new documents to insert")
