
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext   

mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"

spark = SparkSession.builder.appName("newsClassifier").config("spark.mongodb.input.uri", mongodb_connection_string).config("spark.mongodb.output.uri", mongodb_connection_string).config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.11:2.4.1").config("spark.jars", "spark-nlp-spark24_2.11-3.3.0.jar").getOrCreate()

sc = SparkContext.getOrCreate()

df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("database", "news").option("collection", "newsArticles").load()

