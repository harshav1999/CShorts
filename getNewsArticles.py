import json
import urllib.request
from datetime import datetime, timedelta
import pytz
import trafilatura
from dotenv import load_dotenv
import os
load_dotenv()
GNEWS_API = os.getenv("GNEWS_API")


# === GNews API parameters ===
GNEWS_API = GNEWS_API
category = "general"
lang = 'en'
country = "Any"
max = 25
to_date = datetime.now(pytz.utc)
from_date = to_date - timedelta(hours=24)
to_date = to_date.isoformat()
from_date = from_date.isoformat()

url = (
    f"https://gnews.io/api/v4/top-headlines"
    f"?category={category}&lang={lang}&country={country}"
    f"&max={max}&from={from_date}&to={to_date}&apikey={GNEWS_API}"
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

# === Save final JSON with full content ===
with open("news_articles_with_full_content.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=4)

print(f"✅ Done: Saved {len(articles)} articles with full content to 'news_articles_with_full_content.json'")
