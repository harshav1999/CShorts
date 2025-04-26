from getNewsArticles import GNewsArticles
from summarize_azure import SummarizeAzure

if __name__ == "__main__":
    print('hi')
    ## News
    news_obj = GNewsArticles()
    news_obj.run()
    print('bye')
    ## Summarize
    ai_obj = SummarizeAzure()
    ai_obj.summarize()
    ai_obj.thinkchain()