from kafka import KafkaProducer
from kq import Queue
import json 
import requests

news_train_topic = "news-train"

free_news_url = "https://free-news.p.rapidapi.com/v1/search"
free_news_headers = {
	'x-rapidapi-host': "free-news.p.rapidapi.com",
	'x-rapidapi-key': "a074ca3a54mshd2b31882937309fp11ba8bjsndbc6662232d3"
}

free_news_query_keywords = ["India", "Elon musk", "space travel", "floods"]

def get_free_news_response(query, url, headers, r):
	querystring = {"q":query,"lang":"en"}
	
	response = r.get(url, headers=headers, params=querystring).json()

	if("status" in response):
		if(response["status"] == 'ok'):
			articles = []
			for article in response["articles"]:
				article_resopnse = {"title":article['title'], "date":article["published_date"], "summary":article["summary"], "category":article["topic"],"source":article["link"]}
				articles.append(article_resopnse)				
			response = articles	
	else:
		response = []
	return response

producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

queue = Queue(topic=news_train_topic, producer=producer)

for query in free_news_query_keywords:
	queue.enqueue(get_free_news_response, query, free_news_url, free_news_headers, requests)

producer.flush()


