# CShorts

CShorts is a small news-summarization pipeline with a Streamlit front end. It pulls the last 24 hours of top headlines from [GNews](https://gnews.io), scrapes the full article text, stores everything in MongoDB, and uses GPT-4o (via Azure OpenAI) to write a short summary, score each article's importance, and generate follow-up questions. The Streamlit app shows the top-ranked summaries per category.

## Architecture

```
GNews API ──▶ scrape full text ──▶ MongoDB ──▶ summarize ──▶ rank ──▶ Streamlit UI
              (trafilatura)        (News.originalArticles)  (Azure OpenAI, gpt-4o)
```

| Stage | File | What it does |
|---|---|---|
| Scrape | `getNewsArticles.py` | Calls the GNews `top-headlines` endpoint (English, up to 25 articles per request, last 24 hours) for seven feeds: Trending, Business, Tech&AI, Entertainment, Sports, USA and India. Fetches each article URL and extracts the body text with `trafilatura`. Writes a debug snapshot of every request to `data/display_<category>_<country>_<timestamp>.json`. |
| Store | `getNewsArticles.py` | Inserts new articles into the `originalArticles` collection of the `News` database with `is_summarized: 0`. Articles whose title already exists are skipped. |
| Summarize | `summarize_azure.py` | For every article with `is_summarized: 0` and scraped text, asks `gpt-4o` for a 100–150 word summary, saves it as `summary` and sets `is_summarized: 1`. |
| Rank | `rank_articles.py` | For every summarized article in each category, asks `gpt-4o` for a 1–10 score (relevance, importance, impact, timeliness) with a short reason. Saves `ranking_score`, `ranking_reasoning`, `last_ranked` and sets `is_ranked: 1`. Falls back to a score of 5 if the model's reply can't be parsed. |
| ThinkChain | `summarize_azure.py` | For articles with `is_thinkchain: 0`, asks `gpt-4o` for three open-ended questions about the story and saves them as `thinkchain`. |
| UI | `streamlit/app.py` | One tab per category. Each tab shows the 10 highest-scoring articles that are both summarized and ranked, with image, title, source, date and summary. The Trending tab shows articles from all categories. |

`run.py` runs the whole pipeline in order: scrape and store, summarize, rank, ThinkChain.

### Other scripts

- `summarize_chatgpt.py` — alternative summarizer that uses the OpenAI API directly through LangChain (`gpt-4-0125-preview`) instead of Azure. Not called by `run.py`.
- `update_schema.py` — one-off migration that adds `importance_score: 0` and `is_ranked: 0` to documents that lack them.
- `check_db.py` — prints document counts by category, summarization and ranking status, and a sample document.
- `originalNewstoDB.py` — one-off loader that inserts articles from a local `news_articles_with_full_content.json` file into MongoDB. That file is not in the repository (it is git-ignored), so you need to supply your own.

## Setup

Requirements: Python 3, a MongoDB instance (the code was written against MongoDB Atlas), a GNews API key, and an Azure OpenAI resource with a deployment named `gpt-4o`.

```bash
git clone https://github.com/harshav1999/CShorts.git
cd CShorts
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the repository root (it is git-ignored):

```
GNEWS_API=<your GNews API key>
MONGO_URI=<your MongoDB connection string>
AZURE_CHATGPT_ENDPOINT=<your Azure OpenAI endpoint URL>
AZURE_CHATGPT_APIKEY=<your Azure OpenAI API key>
```

| Variable | Used by | Purpose |
|---|---|---|
| `GNEWS_API` | `getNewsArticles.py` | GNews API key |
| `MONGO_URI` | every script and the Streamlit app | MongoDB connection string |
| `AZURE_CHATGPT_ENDPOINT` | `summarize_azure.py`, `rank_articles.py` | Azure OpenAI endpoint |
| `AZURE_CHATGPT_APIKEY` | `summarize_azure.py`, `rank_articles.py` | Azure OpenAI API key |
| `OPENAI_API_KEY` | `summarize_chatgpt.py` only | Read by LangChain's `ChatOpenAI`; only needed if you use the non-Azure summarizer |

## How to run

Run the full pipeline from the repository root (the scraper writes its snapshots to the `data/` directory):

```bash
python run.py
```

Or run the stages individually:

```bash
python getNewsArticles.py   # scrape and store
python summarize_azure.py   # summarize + ThinkChain
python rank_articles.py     # rank
```

Start the UI:

```bash
streamlit run streamlit/app.py
```

To inspect the database state:

```bash
python check_db.py
```

## Future work

- Initialize `is_thinkchain: 0` when articles are inserted. Nothing sets it today, so the ThinkChain step finds no articles unless the field is added by hand, and the UI does not display the questions yet.
- Only rank articles that have not been ranked. `rank_articles.py` currently re-scores every summarized article on each run.
- Skip an article when the summarization call fails instead of continuing with the previous response.
- Schedule the pipeline (cron or a hosted job) rather than running it manually.
- De-duplicate by URL instead of exact title match.
- Stop committing the `data/` debug snapshots, or make them optional.
- Retire or wire up the unused `importance_score` field (the UI sorts by `ranking_score`).
- Add tests and pin a smaller `requirements.txt` with only the packages the code imports.
