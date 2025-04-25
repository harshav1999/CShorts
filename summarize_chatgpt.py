from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")


# === Connect to MongoDB Atlas ===
client = MongoClient(mongo_uri)
db = client["News"]
collection = db["originalArticles"]

# === Initialize GPT-4 Mini ===
llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0.65)

# === Build prompt in system-user format ===
def build_summary_prompt(article_text):
    return [
        SystemMessage(
            content=(
                "You are a creative news editor working for a fast-paced news summarization app. "
                "Your job is to extract the most important information from long articles and write it in such a way that users should not be bored while getting information "
                "in a clear, concise, simple, unbiased format that an average reader can understand quickly."
                "You are free to use emojis or any special characters where needed but dont add them on purpose"
            )
        ),
        HumanMessage(
            content=(
                "Summarize this article in less than 100 words\n\n"
                f"{article_text}\n\n"
            )
        )
    ]

# === Fetch and process articles ===
unsummarized_articles = collection.find({"is_summarized": 0})
count = 0

for article in unsummarized_articles:
    text = article.get("scrap_content")
    if not text:
        continue

    try:
        messages = build_summary_prompt(text)
        result = llm.invoke(messages)
        summary = result.content

        # Update document in MongoDB with summary and is_summarized = 1
        collection.update_one(
            {"_id": article["_id"]},
            {"$set": {
                "summary": summary,
                "is_summarized": 1
            }}
        )

        print(f"✅ Summarized: {article['title']}")
        count += 1

    except Exception as e:
        print(f"❌ Failed to summarize article: {article['title']}")
        print("Error:", str(e))

print(f"\n🎉 Completed: {count} articles summarized and updated to DB.")
