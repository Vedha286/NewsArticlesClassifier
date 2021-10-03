from kafka import KafkaProducer
from kq import Queue
import json
import requests
from datetime import datetime
import schedule
import time
from newsapi import NewsApiClient

news_train_topic = "news-train"

free_news_url = "https://free-news.p.rapidapi.com/v1/search"
free_news_headers = {
    'x-rapidapi-host': "free-news.p.rapidapi.com",
    'x-rapidapi-key': "a074ca3a54mshd2b31882937309fp11ba8bjsndbc6662232d3"
}

free_news_query_keywords = ["India", "Elon musk", "space travel", "floods"]
free_news_query_keywords = ["India"]

news_api = NewsApiClient(api_key='236cd597a4e2440abe9da95ecf2e1f79')


def format_free_news_time(t, datetime):
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

def format_news_api_time(t, datetime):
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")


def get_news_api_response(query, news_api, datetime, format_time):
	
    response = news_api.get_everything(q=query,
                                      language='en',
                                      sort_by='popularity',
				      page_size=2,
                                      page=1)

    if("status" in response):
        if(response["status"] == 'ok'):
            articles = []
            for article in response["articles"]:
                article_resopnse = {"title": article['title'], "date": format_time(
                    article["publishedAt"], datetime), "summary": article["content"], "category": None, "source": article["url"]}
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
                      free_news_headers, requests, datetime, format_free_news_time)
        queue.enqueue(get_news_api_response, query, news_api, datetime, format_news_api_time)
    producer.flush()


# After an interval calling the below functions
schedule.every(20).minutes.do(get_data_from_apis)

while True:
    schedule.run_pending()
    time.sleep(1)


