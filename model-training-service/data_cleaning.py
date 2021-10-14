from pyspark import SparkContext                                                                                        
from pyspark.sql import SparkSession                                                                                    
from pyspark.streaming import StreamingContext   
# import keys as conf

'''
spark = SparkSession \
    .builder \
    .appName("myApp") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/news.newsArticles") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/news.newsArticles") \
    .getOrCreate()

df = spark.read.format("mongo").load()

df.printSchema()
'''
mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"



spark = SparkSession.\
builder.\
appName("pyspark-notebook2").\
config("spark.mongodb.input.uri", mongodb_connection_string).\
config("spark.mongodb.output.uri", mongodb_connection_string).\
config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.0").\
getOrCreate()
df = spark.read.format("com.mongodb.spark.sql.DefaultSource").load()
df.printSchema()



