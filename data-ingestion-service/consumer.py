from kafka import KafkaConsumer
import json 
from pymongo import MongoClient

client = MongoClient("mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority")

db = client.news

try: 
	print("You are connected")
	news_collection =db["newsCollections"]
	db.newsCollections.insert_one({"test":"test1"})
	
	client.close() 
except Exception as e: print(e)


#db = client.news


#consumer = KafkaConsumer(bootstrap_servers=['127.0.0.1:9092'],
#	value_deserializer=lambda m: json.loads(m.decode('utf-32')))

#consumer.subscribe(['news-train'])

#for message in consumer:
#	newAtricle = message.value
#	print (newAtricle)
