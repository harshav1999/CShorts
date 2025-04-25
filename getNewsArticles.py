import json
import urllib.request
from datetime import datetime, timedelta
import pytz
import trafilatura
import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

class GNewsArticles():
    def __init__(self):
        self.to_date = datetime.now(pytz.utc)
        self.from_date = self.to_date - timedelta(hours=24)
        self.from_date = self.from_date.isoformat()
        self.to_date = self.to_date.isoformat()

    def api_request(self, custom_category, category="general", country="Any"):
        max_articles = 25
        GNEWS_API = os.getenv("GNEWS_API")
        lang = 'en'
        url = (
            f"https://gnews.io/api/v4/top-headlines"
            f"?category={category}&lang={lang}&country={country}"
            f"&max={max_articles}&from={self.from_date}&to={self.to_date}&apikey={GNEWS_API}"
        )

        # === Fetch news articles ===
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            articles = data.get("articles", [])

        # === Extract full article content using Trafilatura ===
        for article in articles:
            url = article.get("url")
            scrap_content = None

            if url:
                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    extracted = trafilatura.extract(
                        downloaded,
                        include_comments=False,
                        include_tables=False,
                        include_formatting=False,
                        include_images=False,
                        no_fallback=True,
                        favor_precision=True
                    )
                    scrap_content = extracted

            article["scrap_content"] = scrap_content
            article['custom_category'] = custom_category
        
        # === Save articles to display.json file for refference and testing purposes
        with open(f"data/display_{category}_{country}_{str(self.to_date)}.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)

        return articles

    def send_articles_to_db(self, articles):
        mongo_uri = os.getenv("MONGO_URI")

        if isinstance(articles, dict):
            articles = [articles]  # wrap single object in list

        # === Step 2: Connect to MongoDB Atlas ===
        client = MongoClient(mongo_uri)
        db = client["News"]
        collection = db["originalArticles"]

        # === Step 3: Add is_summarized and check for duplicates ===
        new_docs = []
        for doc in articles:
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

    def run(self):
        ## Trending
        articles = self.api_request(custom_category='Trending')
        self.send_articles_to_db(articles)
        ## Global
        # articles = self.api_request(custom_category='Global', category='world')
        # self.send_articles_to_db(articles)
        ## Business
        articles = self.api_request(custom_category='Business',category='business')
        self.send_articles_to_db(articles)
        ## Tech
        articles = self.api_request(custom_category='Tech&AI', category='technology')
        self.send_articles_to_db(articles)
        ## Entertainment
        articles = self.api_request(custom_category='Entertainment', category='entertainment')
        self.send_articles_to_db(articles)
        ## Sports
        articles = self.api_request(custom_category='Sports', category='sports')
        self.send_articles_to_db(articles)
        ## USA
        articles = self.api_request(custom_category='USA', country='us')
        self.send_articles_to_db(articles)
        ## India
        articles = self.api_request(custom_category='India', country='in')
        self.send_articles_to_db(articles)


if __name__ == "__main__":
    obj = GNewsArticles()
    obj.run()