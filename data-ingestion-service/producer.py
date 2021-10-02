from kafka import KafkaProducer
from kafka.errors import KafkaError
import json 
import requests

free_news_url = "https://free-news.p.rapidapi.com/v1/search"
free_news_headers = {
    'x-rapidapi-host': "free-news.p.rapidapi.com",
    'x-rapidapi-key': "a074ca3a54mshd2b31882937309fp11ba8bjsndbc6662232d3"
}
news_train_topic = "news-train"

producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'],
	value_serializer=lambda v: json.dumps(v).encode('utf-32'))


def get_free_news_response(query, url, headers):
	querystring = {"q":query,"lang":"en"}

	response = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
	
	return response["articles"]

def error_callback(exc):
    raise Exception('Error while sendig data to kafka: {0}'.format(str(exc)))

def write_to_kafka(topic_name, items):
  	#print(items)
	count = 0
	for item in items:
		producer.send(topic_name ,value=item).add_errback(error_callback)
		count = count + 1
  	producer.flush()
	print("Wrote {0} messages into topic: {1}".format(count, topic_name))



mockNews = [{
	'Category':"Crime",
	'description':"something..."
	},{
	"Category":"Movies",
	"description":"something..."
	}]

write_to_kafka(news_train_topic, get_free_news_response("Elon Musk", free_news_url, free_news_headers))
write_to_kafka(news_train_topic, get_free_news_response("Trump", free_news_url, free_news_headers))
write_to_kafka(news_train_topic, get_free_news_response("India", free_news_url, free_news_headers))

