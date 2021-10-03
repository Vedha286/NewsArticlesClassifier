from kafka import KafkaConsumer
import json
from kq import Worker, Message, Job
from pymongo import MongoClient

client = MongoClient("mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority")

db = client.news
news_collection =db["newsCollections"]

def save_all_documents_to_db(doc):

	try: 
		print("Saving " + str(len(doc)) + " documents")
		db.newsCollections.insert_many(doc)
		print("Saved " + str(len(doc)) + " documents")
	
	except Exception as e: 
		print(e)

consumer = KafkaConsumer(bootstrap_servers=['127.0.0.1:9092'], group_id='news_group')

def processResult(status, message, job, result, exception, stacktrace):
	if status == 'success':
		print('Results length: ' + str(len(result)))
		
		if(len(result)>0):
			save_all_documents_to_db(result)
	else:
		print('exception: ' + str(exception))
		print('stacktrace: ' + str(stacktrace))

worker = Worker(topic='news-train', consumer=consumer, callback=processResult)

worker.start()


#client.close() 
