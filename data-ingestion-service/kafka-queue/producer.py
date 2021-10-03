from kafka import KafkaProducer
from kq import Job, Queue
from kafka.errors import KafkaError
import json 
import requests
import base64
import pickle

free_news_url = "https://free-news.p.rapidapi.com/v1/search"
free_news_headers = {
	'x-rapidapi-host': "free-news.p.rapidapi.com",
	'x-rapidapi-key': "a074ca3a54mshd2b31882937309fp11ba8bjsndbc6662232d3"
}
news_train_topic = "news-train"



def get_free_news_response(query, url, headers, r):
	querystring = {"q":query,"lang":"en"}

	response = r.get(url, headers=headers, params=querystring).json()
	print(response)
	return response

producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')
queue = Queue(topic=news_train_topic, producer=producer)


queue.enqueue(get_free_news_response, "Elon Musk", free_news_url, free_news_headers, requests)

