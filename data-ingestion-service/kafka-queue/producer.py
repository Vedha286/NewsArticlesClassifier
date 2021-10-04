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
free_news_daily_limit = 100

newscather_url = "https://api.newscatcherapi.com/v2/search"
newscather_headers = {
    'x-api-key': "5rFJMD3k9h-EPR02GDjEb_3M7eJeJNpEg5Hv7rW15T0"
}

newscather_daily_limit = 1000
times_per_day = 6


query_keywords = [{"keyword":"India", "isComplete":False}, 
{"keyword":"Elon musk", "isComplete":False}, 
{"keyword":"space travel", "isComplete":False}, 
{"keyword":"Vedha", "isComplete":False}]

def format_article_date_time(t, datetime):
    return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

def get_free_news_response(query, url, headers, r, datetime, format_time,time,limit):
    
    articles = []	
    page_count = 1
    stop = False
    page_size = 25
    querystring = {"q": query, "lang": "en", "page_size": page_size, "page": page_count}

    response = r.get(url, headers=headers, params=querystring).json()

    while not stop:
        if("status" in response):
            if(response["status"] == 'ok'):
                print("page_count : " + str(page_count) + "   total_pages: " + str(response["total_pages"]))

                page_count = page_count + 1
                
                for article in response["articles"]:
                    article_resopnse = {"title": article['title'], "date": format_time(article["published_date"], datetime), "summary": article["summary"], "category": article["topic"], "source": article["link"]}
                    articles.append(article_resopnse)
                
                if(page_count == response["total_pages"] or page_count >= limit):
                    stop = True

                else:
                    time.sleep(1)
                    querystring = {"q": query, "lang": "en", "page_size": page_size, "page": page_count}
			
                    response = r.get(url, headers=headers, params=querystring).json()
            elif(response["status"] != 'ok'):
                print(response)
                stop = True
        elif("status" not in response):
            print(response)
            stop = True
    print("=====================================================\n\n\n")

    return articles


def get_newscather_response(query, url, headers, r, datetime, format_time,time,limit):
    
    articles = []	
    page_count = 1
    stop = False
    page_size = 100
    querystring = {"q": query, "lang": "en", "page_size": page_size, "sort_by":"date", "page": page_count}

    response = r.get(url, headers=headers, params=querystring).json()

    while not stop:
        if("status" in response):
            if(response["status"] == 'ok'):
                print("page_count : " + str(page_count) + "   total_pages: " + str(response["total_pages"]))

                page_count = page_count + 1
                
                for article in response["articles"]:
                    article_resopnse = {"title": article['title'], "date": format_time(article["published_date"], datetime), "summary": article["summary"], "category": article["topic"], "source": article["link"]}
                    articles.append(article_resopnse)
                
                if(page_count == response["total_pages"] or page_count >= limit):
                    stop = True

                else:
                    time.sleep(1)
                    querystring = {"q": query, "lang": "en", "page_size": page_size, "sort_by":"date", "page": page_count}
			
                    response = r.get(url, headers=headers, params=querystring).json()
            elif(response["status"] != 'ok'):
                print(response)
                stop = True
        elif("status" not in response):
            stop = True
            print(response)
    print("=====================================================\n\n\n")

    return articles


producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

queue = Queue(topic=news_train_topic, producer=producer)
times_per_day_to_run = 0
# scheduler code starts
def get_data_from_apis():
	global times_per_day_to_run
	for query in query_keywords:
		print(query["keyword"])
		if(not query["isComplete"]):
			
			queue.enqueue(get_free_news_response, query["keyword"], free_news_url,
                      free_news_headers, requests, datetime, format_article_date_time,time, free_news_daily_limit/times_per_day)

			queue.enqueue(get_newscather_response, query["keyword"], newscather_url, newscather_headers, requests, datetime, format_article_date_time, time, newscather_daily_limit/times_per_day)
			query["isComplete"] = True
	producer.flush()
	times_per_day_to_run = times_per_day_to_run + 1	
	if(times_per_day_to_run == 24/times_per_day):
		print("All the keywords ran " + str(times_per_day_to_run))
		times_per_day_to_run = 0
		for query in query_keywords:
			query["isComplete"] = False

# After an interval calling the below functions
schedule.every(10).seconds.do(get_data_from_apis)

while True:
    schedule.run_pending()
    time.sleep(1)


