from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score

from pymongo import MongoClient, errors

import pickle

news_topics = {0: "general news", 1: "sport", 2: "tech", 3: "entertainment", 4: "finance", 5: "politics", 6: "business", 7: "economics", 
               8: "world", 9: "beauty", 10: "gaming", 11:"science", 12:"travel", 13:"energy", 14:"music", 15:"food"}

r_news_topics = {y: x for x, y in news_topics.items()}

print(r_news_topics["energy"])

mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"

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

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import re

ps = PorterStemmer()

def RemoveNonEnglishWords(text):
	text = str(text)
	text = re.sub('[^a-zA-Z]', ' ', text)
	text = text.lower()
	text = text.split()
	text = [ps.stem(word) for word in text if not word in stopwords.words('english')]
	text = ' '.join(text)
	return text



from pyspark import SparkContext
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import IDF
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql import functions as sf

spark = SparkSession.builder.appName("newsClassifier").getOrCreate()
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
# wordsData = tokenizer.transform(train)
# wordsData.show(2)

count = CountVectorizer(inputCol="words", outputCol="rawFeatures")
# model = count.fit(wordsData)
# featurizedData = model.transform(wordsData)
# featurizedData.show(2)

idf = IDF(inputCol="rawFeatures", outputCol="features")
# idfModel = idf.fit(featurizedData)
# rescaledData = idfModel.transform(featurizedData)
# rescaledData.select("features").show(2)


from pyspark.ml.classification import NaiveBayes, RandomForestClassifier, LogisticRegression, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
import numpy as np
from pyspark.ml import Pipeline

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
#fit = nb.fit(train)
#print("nb fit done")
#print("=================================\n")

#pred = fit.transform(test)
#print("nb pred done")
#print("=================================\n")

#pred.show(2)
print("=================================\n")
print("=================================\n")

numFolds = 5
evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")

paramGrid_nb = ParamGridBuilder().addGrid(nb.smoothing, np.linspace(0.3, 10, 10)).build()
print("paramGrid_nb built")

crossval_nb = CrossValidator(estimator=nb, estimatorParamMaps=paramGrid_nb, evaluator=evaluator, numFolds=numFolds)
print("cvModel_nb built")

cvModel_nb = crossval_nb.fit(train)
print("cvModel_nb fit")
print("=================================\n")

best_model_nb = cvModel_nb.bestModel
preds_nb = best_model_nb.transform(test)

preds_nb.select("prediction", "label").show(2)
print("best_model_nb prediction")
print("=================================\n")

accuracy_nb = evaluator.evaluate(preds_nb.select("prediction", "label"))
print("Accuracy (nb) = %g" % accuracy_nb)

print("=================================\n")
print("=================================\n")


paramGrid_rf = ParamGridBuilder().addGrid(rf.numTrees, [5, 15, 20]).build()
print("paramGrid_rf built")

crossval_rf = CrossValidator(estimator=rf, estimatorParamMaps=paramGrid_rf, evaluator=evaluator, numFolds=numFolds)
print("cvModel_rf built")

cvModel_rf = crossval_rf.fit(train)
print("cvModel_rf fit")
print("=================================\n")

best_model_rf = cvModel_rf.bestModel
preds_rf = best_model_rf.transform(test)

preds_rf.select("prediction", "label").show(2)
print("best_model_rf prediction")
print("=================================\n")

accuracy_rf = evaluator.evaluate(preds_rf.select("prediction", "label"))
print("Accuracy (rf) = %g" % accuracy_rf)

print("=================================\n")
print("=================================\n")


paramGrid_ovr = ParamGridBuilder().addGrid(lr.maxIter, [5, 15, 20]).build()
print("paramGrid_ovr built")

crossval_ovr = CrossValidator(estimator=ovr, estimatorParamMaps=paramGrid_ovr, evaluator=evaluator, numFolds=numFolds)
print("cvModel_ovr built")

cvModel_ovr = crossval_ovr.fit(train)
print("cvModel_ovr fit")
print("=================================\n")

best_model_ovr = cvModel_ovr.bestModel
preds_ovr = best_model_ovr.transform(test)

preds_ovr.select("prediction", "label").show(2)
print("best_model_ovr prediction")
print("=================================\n")

accuracy_ovr = evaluator.evaluate(preds_ovr.select("prediction", "label"))
print("Accuracy (ovr) = %g" % accuracy_ovr)




