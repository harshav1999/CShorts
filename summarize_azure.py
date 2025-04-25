import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()

class SummarizeAzure():
    def __init__(self):
        AZURE_CHATGPT_ENDPOINT = os.getenv("AZURE_CHATGPT_ENDPOINT")
        AZURE_CHATGPT_APIKEY = os.getenv("AZURE_CHATGPT_APIKEY")

        self.client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint=AZURE_CHATGPT_ENDPOINT,
            api_key=AZURE_CHATGPT_APIKEY
        )

    def build_summary_prompt(self, article_text):
        return [
                {
                    "role": "system",
                    "content": "You are a world-class journalist and editor known for turning long news articles into clear, engaging summaries that are easy to understand and enjoyable to read.",
                },
                {
                    "role": "user",
                    "content": f"""
Your task is to summarize the following news article into 100 to 150 words.
Instructions:
- Write in a simple, human tone — like you're explaining it to a smart friend.
- Focus on the core message, key facts, and relevant context.
- Keep it interesting and lively; avoid robotic or academic language.
- Do not include a title or headline.
- Don’t mention that it’s a summary — just write as if this is the original text.

Here’s the article content:
---
{article_text}
---"""
                }
            ]

    def summarize(self):
        mongo_uri = os.getenv("MONGO_URI")
        client = MongoClient(mongo_uri)
        db = client["News"]
        collection = db["originalArticles"]
        unsummarized_articles = collection.find({"is_summarized": 0})
        for article in unsummarized_articles:
            text = article.get("scrap_content")
            if not text:
                continue
            try:
                response = self.client.chat.completions.create(
                    messages = self.build_summary_prompt(text),
                    max_tokens=250,
                    temperature=1.0,
                    top_p=1.0,
                    model='gpt-4o'
                )
            except Exception as e:
                print(f"❌ There is error in Azure LLM Api")
                print("Error:", str(e))

            summary = response.choices[0].message.content
            # Update document in MongoDB with summary and is_summarized = 1
            collection.update_one(
                {"_id": article["_id"]},
                {"$set": {
                    "summary": summary,
                    "is_summarized": 1
                }}
            )
            print(f"✅ Summarized: {article['title']}")

    def build_thinkchain_prompt(self, article_text):
        return [
            {
                "role": "system",
                "content": (
                    "You are NewsMind, an inquisitive journalist-bot who helps readers "
                    "think more deeply about current events by posing compelling, "
                    "open-ended questions."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Read the news article below and craft **exactly three** questions "
                    "that ignite curiosity.  The set should:\n"
                    "Questions should not be too lengthy. It should be crisp."
                    "• Reveal the **background / bigger picture** behind the story.\n"
                    "• Explore the **immediate impact** on key people, organisations, or systems.\n"
                    "• Probe the **long-term or ripple effects** that might unfold.\n\n"
                    "Guidelines:\n"
                    "• Questions must be open-ended (start with *How*, *Why*, *What*, *Could*, *In what ways*…).\n"
                    "• Avoid yes/no phrasing and do **not** answer them.\n"
                    "• Keep each question under 25 words and avoid jargon.\n"
                    "• List the five questions on separate lines (no numbering or bullets needed).\n\n"
                    "ARTICLE CONTENT (for context only; do not summarise it):\n"
                    "---\n"
                    f"{article_text}\n"
                    "---"
                ),
            },
        ]

    def thinkchain(self):
        mongo_uri = os.getenv("MONGO_URI")
        client = MongoClient(mongo_uri)
        db = client["News"]
        collection = db["originalArticles"]
        unthinkchain_articles = collection.find({"is_thinkchain": 0})
        for article in unthinkchain_articles:
            text = article.get("scrap_content")
            if not text:
                continue
            try:
                response = self.client.chat.completions.create(
                    messages = self.build_thinkchain_prompt(text),
                    max_tokens=250,
                    temperature=1.0,
                    top_p=1.0,
                    model='gpt-4o'
                )
            except Exception as e:
                print(f"❌ There is error in Azure LLM in thinkchain Api")
                print("Error:", str(e))

            questions = response.choices[0].message.content
            # Update document in MongoDB with summary and is_summarized = 1
            collection.update_one(
                {"_id": article["_id"]},
                {"$set": {
                    "thinkchain": questions,
                    "is_thinkchain": 1
                }}
            )
            print(f"✅ thinkchain: {article['title']}")  

if __name__ == "__main__":
    obj = SummarizeAzure()
    # obj.summarize()
    obj.thinkchain()
        