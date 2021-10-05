from kafka import KafkaConsumer
from kq import Worker
from pymongo import MongoClient, errors

def format_article_date_time(t, datetime):
      return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

def save_all_documents_to_db(docs):

	print(f"Saving {str(len(docs))} documents")
	try:
		client = MongoClient("mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority")
		db = client.news
		stored_docs = db.newsArticles.insert_many(docs, ordered=False, bypass_document_validation=True)
    		
	except errors.BulkWriteError as e:
    		print(f"Articles bulk insertion error {e}")
		
    		panic_list = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
    		if len(panic_list) > 0:
        		print(f"these are not duplicate errors {panic_list}")
	
	finally:
		client.close() 
		print(f"Saved {str(len(stored_docs.inserted_ids))} documents")
		print(f"Filed to save {str(len(docs) - len(stored_docs.inserted_ids))} documents")	

def clean_and_save_articles(result):
      result = list(filter(lambda x: x['summary'] != "", result))
      save_all_documents_to_db(result)

consumer = KafkaConsumer(bootstrap_servers=['127.0.0.1:9092'], group_id='news_group')

def processResult(status, message, job, result, exception, stacktrace):
	if status == 'success':
		print('Results length: ' + str(len(result)))
		print(result)
		if(len(result)>0):
			clean_and_save_articles(result)
	else:
		print('exception: ' + str(exception))
		print('stacktrace: ' + str(stacktrace))

worker = Worker(topic='news-train', consumer=consumer, callback=processResult)

worker.start()


