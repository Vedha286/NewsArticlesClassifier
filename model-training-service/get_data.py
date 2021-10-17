from pymongo import MongoClient, errors
from pyspark import SparkContext                                                                                        
from pyspark.sql import SparkSession                                                                                    
from pyspark.streaming import StreamingContext   
from pyspark.sql import SQLContext

def handle_rdd(rdd):
	if not rdd.isEmpty():
		print(rdd)

mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"

client = MongoClient(mongodb_connection_string)
db = client.news


print('/n==================================================================/n')
spark = SparkSession.builder.appName("newsClassifier").getOrCreate()
print('/n==================================================================/n')
spark.sparkContext.setLogLevel('WARN')
print('/n==================================================================/n')

newsArticles = db.newsArticles.find({}, {"_id":0})
newsArticlesArr = []
for newsArticle in newsArticles:
	#print(newsArticle)
	newsArticlesArr.append(newsArticle)
#df = spark.createDataFrame(newsArticlesArr)

#df.show()
print(len(newsArticlesArr))
rdd = spark.sparkContext.parallelize(newsArticlesArr)
dfFromRDD1 = rdd.toDF()
dfFromRDD1.printSchema()
rdd.foreachRDD(handle_rdd)



