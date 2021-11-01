from kafka import KafkaConsumer
from kq import Worker
from pymongo import MongoClient, errors
import keys as conf

def format_article_date_time(t, datetime):
      return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

def save_all_documents_to_db(docs):
      print("Saving " + str(len(docs)) + " documents")

      try:
            client = MongoClient(conf.mongodb_connection_string)
            stored_docs = 0
            failed_docs = 0
            db = client.news
            for doc in docs:
                   try:
                        db.newsArticles.insert_one(doc)
                        stored_docs = stored_docs + 1
                   except Exception as e:
                        failed_docs = failed_docs + 1
                        print("Failed to save " + str(doc) + " with error: " + str(e))
                        
            print("Saved " + str(stored_docs) + " documents")
            print("Failed to save " + str(failed_docs) + " documents")	

      except errors.BulkWriteError as e:
            print("Articles bulk insertion error " + str(e))		
            panic_list = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
            if len(panic_list) > 0:
                  print("These are not duplicate errors " + str(panic_list))

      finally:
            client.close() 

def replace_element(n, key, value):
      n[key] = value
      return n

def clean_and_save_articles(result):
      result = list(filter(lambda elem: elem["summary"] != "", result))
      modify_results = list(filter(lambda elem: elem["category"] == "news", result))
      result = list(filter(lambda elem: elem["category"] != "news", result))
      result = result + list(map(lambda n: replace_element(n, "category","general news"), modify_results))
      save_all_documents_to_db(result)
      return 

consumer = KafkaConsumer(bootstrap_servers=['127.0.0.1:9092'], group_id='news_group')

def processResult(status, message, job, result, exception, stacktrace):
      if status == 'success':
            print('Results length: ' + str(len(result)))
            if(len(result)>0):
                  clean_and_save_articles(result)
      else:
            print('exception: ' + str(exception))
            print('stacktrace: ' + str(stacktrace))

worker = Worker(topic='news-train', consumer=consumer, callback=processResult)

worker.start()


