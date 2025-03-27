import streamlit as st
from pymongo import MongoClient
import datetime
from dotenv import load_dotenv
import os
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# === MongoDB Setup ===
client = MongoClient(mongo_uri)
db = client["News"]
collection = db["originalArticles"]

# === Streamlit Page Config ===
st.set_page_config(page_title="🗞️ CShorts - Summarized News", layout="wide")
st.title("🗞️ CShorts - Summarized News")
st.markdown("Stay updated with the latest summarized news, all in one place.")

# === Fetch summarized articles ===
articles = collection.find({"is_summarized": 1}).sort("publishedAt", -1)

# === UI Layout ===
for article in articles:
    with st.container():
        col1, col2 = st.columns([1, 4])

        with col1:
            st.image(article.get("image", "https://via.placeholder.com/150"), use_container_width=True)

        with col2:
            st.markdown(f"### {article.get('title', 'No Title')}")
            st.markdown(f"**Source:** {article['source'].get('name', 'Unknown')}  |  📅 {article.get('publishedAt', '')[:10]}")
            st.markdown(f"{article.get('summary', 'No summary available.')}")

        st.markdown("---")

# === Footer ===
st.markdown("<br><center>Made with ❤️ </center>", unsafe_allow_html=True)
