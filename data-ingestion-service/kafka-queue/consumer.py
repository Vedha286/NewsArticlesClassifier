from kafka import KafkaConsumer
import json
import base64
import requests
from kq import Worker
import pickle


consumer = KafkaConsumer(bootstrap_servers=['127.0.0.1:9092'],
	value_deserializer=lambda m: json.loads(m.decode('utf-32')))


worker = Worker(topic='news-train', consumer=consumer, deserializer=pickle.loads)
worker.start()

consumer.subscribe(['news-train'])

for message in consumer:
	newAtricle = message.value
	print (newAtricle)
