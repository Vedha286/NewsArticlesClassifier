from pyspark import SparkContext                                                                                        
from pyspark.sql import SparkSession                                                                                    
from pyspark.streaming import StreamingContext   
from pyspark.sql import SQLContext
from pyspark.streaming.kafka import KafkaUtils
import py4j

print(dir(py4j))
def handle_rdd(rdd):
	if not rdd.isEmpty():
			print(rdd)
	else:
		print('rdd is empty' )
		print(rdd)

sc = SparkContext(appName ="newsClassifier")
ssc = StreamingContext(sc, 5)
spark = SparkSession.builder.appName("newsClassifier").getOrCreate()

spark.sparkContext.setLogLevel('WARN')

ks = KafkaUtils.createDirectStream(ssc, ['news-articles'], {'bootstrap.servers': '127.0.0.1:9092'})
print(ks)

lines = ks.map(lambda x: json.load(x[1]).encode('utf-8'))
print(lines)
transform = lines.map(lambda record : (print(record)))
transform.foreachRDD(handle_rdd)

ssc.start()
ssc.awaitTermination()


