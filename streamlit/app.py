import streamlit as st
from pymongo import MongoClient
import os, datetime
from dotenv import load_dotenv

# ——— 1) ENV + DB ————————————————————————————————————————————
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

client      = MongoClient(mongo_uri)
db          = client["News"]
collection  = db["originalArticles"]

# ——— 2) PAGE CONFIG ————————————————————————————————————————
st.set_page_config(page_title="🗞️ CShorts - Summarized News",
                   layout="wide",
                   initial_sidebar_state="collapsed")   # hide the empty sidebar

st.title("🗞️ CShorts - Summarized News")
st.caption("Stay updated with the latest summarized news, all in one place.")

# ——— 3) TOP NAV BAR (categories come from custom_category) ——-
CATEGORIES = ["Trending", "Business", "Tech&AI", "Entertainment",
              "Sports", "USA", "India"]

# Create tabs for categories
tabs = st.tabs(CATEGORIES)

# ——— 4) QUERY ARTICLES ————————————————————————————————
for i, tab in enumerate(tabs):
    with tab:
        category = CATEGORIES[i]
        query = {
            "is_summarized": 1, 
            "is_ranked": 1
        }
        if category != "Trending":                       # "Trending" = show all
            query["custom_category"] = category

        # Get articles from the last 24 hours
        one_day_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        query["publishedAt"] = {"$gte": one_day_ago.isoformat()}

        # Sort by publishedAt in descending order and limit to 20 most recent articles
        articles = collection.find(query).sort("publishedAt", -1).limit(20)

        # ——— 5) RENDER —————————————————————————————————————————————
        for article in articles:
            with st.container():
                col1, col2 = st.columns([1, 4], gap="large")

                # — image —
                with col1:
                    st.image(
                        article.get(
                            "image",
                            "https://via.placeholder.com/150?text=No+Image"),
                        use_container_width=True
                    )

                # — text —
                with col2:
                    st.markdown(f"### {article.get('title', 'No Title')}")
                    st.markdown(
                        f"**Source:** {article['source'].get('name','Unknown')}"
                        f" &nbsp; | &nbsp; 📅 {article.get('publishedAt','')[:10]}"
                    )
                    st.markdown(article.get('summary', '*No summary available.*'))

                st.divider()  # prettier than '---'

# ——— 6) FOOTER ————————————————————————————————————————————
st.markdown(
    "<br><center>Made with ❤️ <br> Feedback is highly appreciated: harsha.autodub@gmail.com"
    f"</center>",
    unsafe_allow_html=True
)
