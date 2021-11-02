from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient, errors

import pickle

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import re

from pyspark import SparkContext
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import IDF
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql import functions as sf
from pyspark.ml.classification import NaiveBayes, RandomForestClassifier, LogisticRegression, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
import numpy as np
from pyspark.ml import Pipeline

ps = PorterStemmer()

def RemoveNonEnglishWords(text):
	text = str(text)
	text = re.sub('[^a-zA-Z]', ' ', text)
	text = text.lower()
	text = text.split()
	text = [ps.stem(word) for word in text if not word in stopwords.words('english')]
	text = ' '.join(text)
	return text

news_topics = {0: "general news", 1: "sport", 2: "tech", 3: "entertainment", 4: "finance", 5: "politics", 6: "business", 7: "economics", 
               8: "world", 9: "beauty", 10: "gaming", 11:"science", 12:"travel", 13:"energy", 14:"music", 15:"food"}

r_news_topics = {y: x for x, y in news_topics.items()}

mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"

news_model_file = "../models/new_nb.pkl"


def load_model():
      try:
            pickle.load(open(news_model_file, "rb"))
      except Exception as e:
            train()

def train():
	client = MongoClient(mongodb_connection_string)
	db = client.news
	print('Getting data')
	newsArticles = db.newsArticles.find({}, {"_id":0, "date":0, "source":0}).limit(1000)
	client.close() 

	newsArticlesArr = []
	for newsArticle in newsArticles:
		newsArticlesArr.append(newsArticle)

	print(len(newsArticlesArr))


	corpus=[]
	true_preds = []
	print("=================================")
	print("=================================")

	spark = SparkSession.builder.master("local").appName("newsClassifier").getOrCreate()
	spark.sparkContext.setLogLevel('WARN')

	df = spark.createDataFrame(Row(RemoveNonEnglishWords(x['title']), RemoveNonEnglishWords(x['summary']), r_news_topics[x["category"]] ) for x in newsArticlesArr)
	df = df.withColumn("sen", sf.concat(sf.col('_1'), sf.lit(' '), sf.col('_2')))
	df = df.drop("_1")
	df = df.drop("_2")
	df = df.withColumnRenamed("_3", "label")
	# df = df.rdd.map(lambda x: RemoveNonEnglishWords(x['sen']))
	df = df.na.fill("test")
	df.show(5)
	print("partitions: " + str(df.rdd.getNumPartitions()))

	tokenizer = Tokenizer(inputCol="sen", outputCol="words")
	count = CountVectorizer(inputCol="words", outputCol="rawFeatures")
	idf = IDF(inputCol="rawFeatures", outputCol="features")

	pipeline = Pipeline(stages=[tokenizer, count, idf])

	rescaledData = pipeline.fit(df).transform(df).select("features", "label")
	print("rescaledData")
	rescaledData.show(2)
	print("=================================\n")

	train, test = rescaledData.randomSplit([0.7, 0.3])

	print("train")
	train.show(2)
	print("=================================\n")
	print("partitions train: " + str(train.rdd.getNumPartitions()))
	train.repartition(20)
	print("partitions train: " + str(train.rdd.getNumPartitions()))

	print("test")
	test.show(2)
	print("=================================\n")


	nb = NaiveBayes()
	rf = RandomForestClassifier(numTrees=10)
	lr = LogisticRegression(maxIter = 10)
	ovr = OneVsRest(classifier=lr)

	print("=================================\n")
	print("=================================\n")

	numFolds = 5
	evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")

	paramGrid_nb = ParamGridBuilder().addGrid(nb.smoothing, np.linspace(0.3, 10, 20)).build()
	print("paramGrid_nb built")

	paramGrid_ovr = ParamGridBuilder().addGrid(lr.maxIter, [5, 15, 20]).build()
	print("paramGrid_ovr built")

	paramGrid_rf = ParamGridBuilder().addGrid(rf.numTrees, [2, 3, 4]).build()
	print("paramGrid_rf built")

	paramGrids = [
	      paramGrid_nb, 
	      paramGrid_rf, 
	      paramGrid_ovr
	]
	models = [
	      nb, 
	      rf, 
	      ovr
	]
	models_names = [
	      "nb",
	      "rf",
	      "ovr"
	]

	accuracies = []	
	best_models = []

	for i in range(0, len(models_names)):
		crossval_model = CrossValidator(estimator=models[i], estimatorParamMaps=paramGrids[i], evaluator=evaluator, numFolds=numFolds)
		print("cv Model built: " + models_names[i])

		print("Training model: " + models_names[i])
		model = crossval_model.fit(train)

		print("Got the best model...")
		best_model = model.bestModel
		best_models.append(best_model)

		print("Predicting model: " + models_names[i])
		preds = best_model.transform(test)

		preds.select("prediction", "label").show(2)
	
		accuracy = evaluator.evaluate(preds.select("prediction", "label"))
		accuracies.append(accuracy)
		print("Accuracy of " + models_names[i] + " = %g" % accuracy)

		print("=================================\n")

	max_accuracy = max(accuracies)
	model_index = accuracies.index(max_accuracy)
	print("index: " + str(model_index))

train()

