from getNewsArticles import GNewsArticles
from summarize_azure import SummarizeAzure
from rank_articles import rank_articles_by_category

if __name__ == "__main__":
    print('hi')
    ## News
    news_obj = GNewsArticles()
    news_obj.run()
    print('bye')
    ## Summarize
    ai_obj = SummarizeAzure()
    ai_obj.summarize()
    rank_articles_by_category()
    ai_obj.thinkchain()