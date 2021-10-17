from kafka import KafkaProducer
import schedule
import time
import pandas as pd
from pymongo import MongoClient, errors
import json

times_per_day = 1
mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"
producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def get_data_from_db():
	client = MongoClient(mongodb_connection_string)
	db = client.news	
	newsArticles = list(db.newsArticles.find({}, {"_id":0, "date":0}))
	print(type(newsArticles))
	producer.send('news-articles', newsArticles)
	print('sent data')
	client.close() 
            

	producer.flush()
get_data_from_db()

#schedule.every(24/times_per_day).seconds.do(get_data_from_db)

#while True:
#    schedule.run_pending()
#    time.sleep(1)

