from kafka import KafkaProducer
from kafka.errors import KafkaError
import json 

def error_callback(exc):
    raise Exception('Error while sendig data to kafka: {0}'.format(str(exc)))

def write_to_kafka(topic_name, items):

  	print(items)
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

producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'],
	value_serializer=lambda v: json.dumps(v).encode('utf-32'))
write_to_kafka("susy-train", mockNews)

