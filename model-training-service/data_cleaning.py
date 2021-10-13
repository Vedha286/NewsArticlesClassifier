from pyspark import SparkContext                                                                                        
from pyspark.sql import SparkSession                                                                                    
from pyspark.streaming import StreamingContext   
import keys as conf

'''
my_spark = SparkSession \
    .builder \
    .appName("myApp") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/news.newsArticles") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/news.newsArticles") \
    .getOrCreate()

df = spark.read.format("mongo").load()

df.printSchema()
'''

spark = SparkSession.\
builder.\
appName("pyspark-notebook2").\
master("spark://spark-master:7077").\
config("spark.executor.memory", "1g").\
config("spark.mongodb.input.uri", conf.mongodb_connection_string).\
config("spark.mongodb.output.uri", conf.mongodb_connection_string).\
config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.0").\
getOrCreate()
df = spark.read.format("mongo").load()
df.printSchema()
