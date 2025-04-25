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

# horizontal=True gives us a very light “navbar” look & feel
category = st.radio(
    "",
    CATEGORIES,
    index=0,
    horizontal=True,
    label_visibility="collapsed"  # hide the radio header text
)

# ——— (optional) tiny CSS tweak so it really looks like a nav bar —
st.markdown(
    """
    <style>
    div.stRadio > label { display: flex; justify-content: center; }
    div.stRadio > label div { 
        padding: 0.4rem 1rem; border-radius: 0.5rem;
        font-weight: 600; cursor: pointer;
    }
    /* highlight the active tab */
    div.stRadio > label div[data-selected="true"] {
        background: rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ——— 4) QUERY ARTICLES ————————————————————————————————
query = {"is_summarized": 1}                     # always summarized
if category != "Trending":                       # “Trending” = show all
    query["custom_category"] = category

articles = collection.find(query).sort("publishedAt", -1)

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
