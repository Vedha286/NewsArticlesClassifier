
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
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
from pyspark.ml.classification import NaiveBayes, RandomForestClassifier, LogisticRegression, OneVsRest, NaiveBayesModel, RandomForestClassificationModel, OneVsRestModel
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
import numpy as np
import pandas as pd
from pyspark.ml import Pipeline
import mlflow
import os
import shutil

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

news_model_file = "../models/news_nb.pkl"


def load_model():
      try:
            pickle.load(open(news_model_file, "rb"))
      except Exception as e:
            train()

def train():
	client = MongoClient(mongodb_connection_string)
	db = client.news
	print('Getting data')
	newsArticles = db.newsArticles.find({}, {"_id":0, "date":0, "source":0}).limit(10)
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
	spark.conf.set("spark.driver.allowMultipleContexts", "true")
	spark.sparkContext.setLogLevel('WARN')

	df = spark.createDataFrame(Row(RemoveNonEnglishWords(str(x['title']) + " " + str(x['summary'])), r_news_topics[x["category"]] ) for x in newsArticlesArr)
	df = df.withColumnRenamed("_1", "sen")
	df = df.withColumnRenamed("_2", "label")
	df = df.na.fill("test")
	df.show(5)
	print("partitions: " + str(df.rdd.getNumPartitions()))

	tokenizer = Tokenizer(inputCol="sen", outputCol="words")
	count = CountVectorizer(inputCol="words", outputCol="rawFeatures")
	idf = IDF(inputCol="rawFeatures", outputCol="features")

	pipeline = Pipeline(stages=[tokenizer, count, idf])

	transformer = pipeline.fit(df)
	rescaledData =transformer.transform(df).select("features", "label")
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
	rf = RandomForestClassifier(numTrees=5)
	lr = LogisticRegression(maxIter = 4)
	ovr = OneVsRest(classifier=lr)

	print("=================================\n")
	print("=================================\n")

	numFolds = 5
	evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")

	paramGrid_nb = ParamGridBuilder().addGrid(nb.smoothing, np.linspace(0.3, 2, 1)).build()
	

	print("paramGrid_nb built")

	paramGrid_ovr = ParamGridBuilder().addGrid(lr.maxIter, [1, 3, 2]).build()
	print("paramGrid_ovr built")

	paramGrid_rf = ParamGridBuilder().addGrid(rf.numTrees, [2, 3, 1]).build()

	print("paramGrid_rf built")

	paramGrids = [
	      paramGrid_nb, 
#	      paramGrid_rf, 
#	      paramGrid_ovr
	]
	models = [
	      nb, 
#	      rf, 
#	      ovr
	]
	models_names = [
	      "nb",
#	      "rf",
#	      "ovr"
	]

	accuracies = []	
	best_models = []

	for i in range(0, len(models_names)):
		crossval_model = CrossValidator(estimator=models[i], estimatorParamMaps=paramGrids[i], evaluator=evaluator, numFolds=numFolds)
		#model =	crossval_model.fit(train)
		
		print("cv Model built: " + models_names[i])
		print("Training model: " + models_names[i])
		model = crossval_model.fit(train)
		
		print("Got the best model...")
		best_model = model.bestModel
		
		print(best_model.explainParams())
#		model_pipeline = Pipeline(stages=[best_model])
		best_models.append(best_model)
#		model_pipeline = Pipeline(stages=[best_model])
#		model_pipeline.save("sample-model")

		print("Predicting model: " + models_names[i])
		preds = model.transform(test)

		preds.select("prediction", "label").show(2)
	
		accuracy = evaluator.evaluate(preds.select("prediction", "label"))
		accuracies.append(accuracy)
		mlflow.log_metric('test_' + evaluator.getMetricName(), accuracy) 
		# Log the best model.
#		mlflow.spark.log_model(spark_model=best_model, artifact_path='best-model') 

		print("Accuracy of " + models_names[i] + " = %g" % accuracy)

		print("=================================\n")
		if os.path.exists("model"+models_names[i]):
	                shutil.rmtree("model"+models_names[i], ignore_errors=True)
        
       

	max_accuracy = max(accuracies)
	model_index = accuracies.index(max_accuracy)
	print("index: " + str(model_index))
#	print("Using model " + models_names[model_index])
#	print("Accuracy %g" % accuracies[model_index])
#	preds = best_models[model_index].transform(test)
#	spark.sparkContext.stop()
	preds.show(5)
	print("=================================\n")	
	print("=================================\n")
	print("=================================\n")
#	with mlflow.start_run():
		# Run the cross validation on the training dataset. The cv.fit() call returns the best model it found.
	cvModel = nb.fit(train)

		# Evaluate the best model's performance on the test dataset and log the result.
#	test_metric = evaluator.evaluate(cvModel.transform(test))
	filename = 'model'+models_names[model_index]
	if os.path.exists(filename):
		shutil.rmtree(filename, ignore_errors=True)
	else:
		print("Can not delete the file as it doesn't exists")
	best_models[model_index].save(filename)


	if os.path.exists("modelovr"):
		m = OneVsRestModel.load(filename)
		rr = m.transform(test)
		print(rr)
	elif os.path.exists("modelnb"):
		m = NaiveBayesModel.load(filename)
		rr = m.transform(test)
		print(rr)
	else:
		m = RandomForestClassificationModel.load(filename)
		rr = m.transform(test)
		print(rr)
	df_test = pd.DataFrame(np.array([["test"]]),
                   columns=['sen'])

#	df_test = spark.createDataFrame(Row("Test"))
#	df_test = df_test.withColumnRenamed("_1", "sen")

	df_test = spark.createDataFrame([
		(0, "Hi I heard about Spark"),
	], ["id", "sen"])
	df_test.show()
	test1 = transformer.transform(df_test)
	print(test1)
	p1 = m.transform(test1)
	p1.select("prediction").show()
#	pickle.dump(cvModel, open(filename, 'wb'))
#		mlflow.log_metric('test_' + evaluator.getMetricName(), test_metric) 
		# Log the best model.
#		mlflow.spark.log_model(spark_model=cvModel.bestModel, artifact_path='best-model') 
#	mlflow.spark.save_model(nb, "spark-model")	
#	best_models[model_index].save("pipline_model")
#	mlflow.spark.save_model(best_models[model_index], "spark_model")
#	pickle.dump(best_models[model_index], open("news_nb.pkl", "wb"))
	print("Saved model...")

train()

