from kafka import KafkaProducer
from kq import Queue
import requests
from datetime import datetime
import schedule
import time
import pandas as pd
import keys as conf

news_train_topic = "news-train"

free_news_url = "https://free-news.p.rapidapi.com/v1/search"
free_news_headers = {
    'x-rapidapi-host': "free-news.p.rapidapi.com",
    'x-rapidapi-key': conf.rapidapi_key
}
free_news_daily_limit = 100

newscather_url = "https://api.newscatcherapi.com/v2/search"
newscather_headers = {
    'x-api-key': conf.newscather_key
}

newscather_daily_limit = 1000
times_per_day = 1

time_string_format = "%Y-%m-%d %H:%M:%S"

def format_article_date_time(t, datetime):
    return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

def get_free_news_response(query, url, headers, r, time, limit, handle_error_response, format_response, isLimtReached, time_string_format, datetime):
    
    articles = []	
    page_count = 1
    stop = False
    page_size = 25
    querystring = {"q": query, "lang": "en", "page_size": page_size, "page": page_count}

    response = r.get(url, headers=headers, params=querystring).json()

    while not stop:
        if(handle_error_response(response)):
            print("page_count : " + str(page_count) + " total_pages: " + str(response['total_pages']))
            page_count = page_count + 1
                
            for article in response["articles"]:
                articles.append(format_response(article, time_string_format, datetime))
                
            if(isLimtReached(limit, page_count, response["total_pages"])):
                stop = True

            else:
                time.sleep(1)
                querystring = {"q": query, "lang": "en", "page_size": page_size, "page": page_count}
                response = r.get(url, headers=headers, params=querystring).json()

        else:
            stop = True

    print("=====================================================\n\n\n")

    return articles

def handle_error_response(response):
    if("status" in response):
        if(response["status"] == 'ok'):
            return response
    print("Response error: " + str(response))
    return None

def format_response(article, time_string_format, datetime):
    return {"title": article['title'], "date": datetime.strptime(article["published_date"], time_string_format), "summary": article["summary"], "category": article["topic"], "source": article["link"]}

def get_newscather_response(query, url, headers, r, time, limit, handle_error_response, format_response, isLimtReached, time_string_format, datetime):
    
    articles = []	
    page_count = 1
    stop = False
    page_size = 100
    querystring = {"q": query, "lang": "en", "page_size": page_size, "sort_by":"date", "page": page_count}

    response = r.get(url, headers=headers, params=querystring).json()

    while not stop:
        if(handle_error_response(response)):
            print("page_count : " + str(page_count) + " total_pages: " + str(response['total_pages']))
            page_count = page_count + 1
                
            for article in response["articles"]:
                articles.append(format_response(article, time_string_format, datetime))
                
            if(isLimtReached(limit, page_count, response["total_pages"])):
                stop = True

            else:
                time.sleep(1)
                querystring = {"q": query, "lang": "en", "page_size": page_size, "sort_by":"date", "page": page_count}
                response = r.get(url, headers=headers, params=querystring).json()
                
        else:
            stop = True
        
    print("=====================================================\n\n\n")

    return articles

def isLimtReached(limit, page_count, total_pages):
    return page_count == total_pages or page_count >= limit


producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

queue = Queue(topic=news_train_topic, producer=producer)
# scheduler code starts
def get_data_from_apis():
	queue.enqueue(get_free_news_response, "*", free_news_url, free_news_headers, requests, time, free_news_daily_limit/times_per_day, handle_error_response, format_response, isLimtReached, time_string_format, datetime)
	queue.enqueue(get_newscather_response, "*", newscather_url, newscather_headers, requests, time, newscather_daily_limit/times_per_day, handle_error_response, format_response, isLimtReached, time_string_format, datetime)

	producer.flush()
	

# After an interval calling the below functions
schedule.every(24/times_per_day).hours.do(get_data_from_apis)
#schedule.every(24/times_per_day).hours.do(get_data_from_apis)

while True:
    schedule.run_pending()
    time.sleep(1)


