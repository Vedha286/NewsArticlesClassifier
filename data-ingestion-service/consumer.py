from kafka import KafkaConsumer
import json 

consumer = KafkaConsumer(bootstrap_servers=['127.0.0.1:9092'],
	value_deserializer=lambda m: json.loads(m.decode('utf-32')))

consumer.subscribe(['news-train'])

for message in consumer:
	newAtricle = message.value
	print (newAtricle)
