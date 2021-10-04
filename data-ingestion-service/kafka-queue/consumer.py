from kafka import KafkaConsumer
import json
from kq import Worker, Message, Job
from pymongo import MongoClient

client = MongoClient("mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority")

db = client.news
news_collection =db["newsArticles"]
db_errors = []

def save_all_documents_to_db(docs):

	print("Saving " + str(len(docs)) + " documents")
	pass_count = 0
	fail_count = 0
	for doc in docs:
		try: 
			db.newsArticles.insert_one(doc)

			pass_count = pass_count + 1
	
		except Exception as e: 
			db_errors.append(e)
			fail_count = fail_count + 1
	print("Saved " + str(pass_count) + " documents")
	print(str(fail_count) + " documents failed to save")

consumer = KafkaConsumer(bootstrap_servers=['127.0.0.1:9092'], group_id='news_group')

def processResult(status, message, job, result, exception, stacktrace):
	if status == 'success':
		print('Results length: ' + str(len(result)))
		print(result)
		
		if(len(result)>0):
			save_all_documents_to_db(result)
	else:
		print('exception: ' + str(exception))
		print('stacktrace: ' + str(stacktrace))

worker = Worker(topic='news-train', consumer=consumer, callback=processResult)

worker.start()


#client.close() 
