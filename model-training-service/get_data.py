from pymongo import MongoClient, errors
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext   
from prepare_data import RemoveNonEnglishWords, Vectorize

mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"

client = MongoClient(mongodb_connection_string)
db = client.news

spark = SparkSession.builder.appName("newsClassifier").getOrCreate()
spark.sparkContext.setLogLevel('WARN')

newsArticles = db.newsArticles.find({}, {"_id":0, "date":0, "source":0})
newsArticlesArr = []
for newsArticle in newsArticles:
	newsArticlesArr.append(newsArticle)

print('Got ' + str(len(newsArticlesArr)) + ' records')

df = spark.createDataFrame(newsArticlesArr)

rddX = df.rdd.map(lambda x: str(x['title']) + ' ' + str(x['summary']))
rddX = rddX.map(lambda x: RemoveNonEnglishWords(x))
print('Removed non english words')

X = Vectorize(rddX.collect())
print('Vectorized X data shape:')
print(X.shape)

rddY = df.rdd.map(lambda x: str(x['category']))
print('Y data shape (showing top 5):')
print(rddY.collect()[:5])


