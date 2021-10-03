from kafka import KafkaProducer
from kq import Queue
import json
import requests
from datetime import datetime
import schedule
import time

news_train_topic = "news-train"

free_news_url = "https://free-news.p.rapidapi.com/v1/search"
free_news_headers = {
    'x-rapidapi-host': "free-news.p.rapidapi.com",
    'x-rapidapi-key': "a074ca3a54mshd2b31882937309fp11ba8bjsndbc6662232d3"
}

free_news_query_keywords = ["India", "Elon musk", "space travel", "floods"]


'''
pip install newsapi-python
from newsapi import NewsApiClient

# Init
newsapi = NewsApiClient(api_key='236cd597a4e2440abe9da95ecf2e1f79')

all_articles = newsapi.get_everything(q='bitcoin',
                                      sources='bbc-news,the-verge',
                                      domains='bbc.co.uk,techcrunch.com',
                                      from_param='2017-12-01',
                                      to='2017-12-12',
                                      language='en',
                                      sort_by='relevancy',
                                      page=2)
                                      
                                      '''
def format_time(t, datetime):
    return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")


def get_free_news_response(query, url, headers, r, datetime, format_time):
    querystring = {"q": query, "lang": "en", "page_size": 2}

    response = r.get(url, headers=headers, params=querystring).json()

    if("status" in response):
        if(response["status"] == 'ok'):
            articles = []
            for article in response["articles"]:
                article_resopnse = {"title": article['title'], "date": format_time(
                    article["published_date"], datetime), "summary": article["summary"], "category": article["topic"], "source": article["link"]}
                articles.append(article_resopnse)
            response = articles
    else:
        response = []
    return response


producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

queue = Queue(topic=news_train_topic, producer=producer)

# scheduler code starts
def get_data_from_apis():
    for query in free_news_query_keywords:
        queue.enqueue(get_free_news_response, query, free_news_url,
                      free_news_headers, requests, datetime, format_time)
    producer.flush()


# After an interval calling the below functions
schedule.every(20).minutes.do(get_data_from_apis)

while True:
    schedule.run_pending()
    time.sleep(1)


