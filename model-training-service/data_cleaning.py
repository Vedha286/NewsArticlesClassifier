from pyspark import SparkContext                                                                                        
from pyspark.sql import SparkSession                                                                                    
from pyspark.streaming import StreamingContext                                                                          

my_spark = SparkSession \
    .builder \
    .appName("myApp") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/news.newsArticles") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/news.newsArticles") \
    .getOrCreate()

df = spark.read.format("mongo").load()

df.printSchema()

