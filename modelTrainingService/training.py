
from pymongo import MongoClient, errors
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
from pyspark.ml.classification import NaiveBayes, RandomForestClassifier, LogisticRegression, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
import numpy as np
import pandas as pd
from pyspark.ml import Pipeline
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

model_dir = 'models/model-test'
spark = SparkSession.builder.master("local").appName("newsClassifier").getOrCreate()
spark.conf.set("spark.driver.allowMultipleContexts", "true")
spark.sparkContext.setLogLevel('WARN')
tokenizer = Tokenizer(inputCol="sen", outputCol="words")
count = CountVectorizer(inputCol="words", outputCol="rawFeatures")
idf = IDF(inputCol="rawFeatures", outputCol="features")
pipeline = Pipeline(stages=[tokenizer, count, idf])
accuracies = [] 
best_models = []

def load_model():
      if not os.path.exists(model_dir+"ovr") and not os.path.exists(model_dir+"nb") and not os.path.exists(model_dir+"rf"):
            train()
def train():
        client = MongoClient(mongodb_connection_string)
        db = client.news
        print('Getting data')
        newsArticles = db.newsArticles.find({}, {"_id":0, "date":0, "source":0})
        client.close()
        newsArticlesArr = []
        for newsArticle in newsArticles:
                newsArticlesArr.append(newsArticle)
        print("Got " + str(len(newsArticlesArr)) + " records")

        print("=================================")
        print("=================================")
        
        df = spark.createDataFrame(Row(RemoveNonEnglishWords(str(x['title']) + " " + str(x['summary'])), r_news_topics[x["category"]] ) for x in newsArticlesArr)
        df = df.withColumnRenamed("_1", "sen")
        df = df.withColumnRenamed("_2", "label")
        df = df.na.fill("test")
        
        
        transformer = pipeline.fit(df)
        transformer.write().overwrite().save(model_dir+"pipeline")

        rescaledData =transformer.transform(df).select("features", "label")

        print("=================================\n")
        train, test = rescaledData.randomSplit([0.7, 0.3])
        print("train data")
        train.show(2)
        print("=================================\n")
        print("=================================\n")
       
        print("test data")
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
        paramGrid_nb = ParamGridBuilder().addGrid(nb.smoothing, np.linspace(5,3, 1)).build()
        
        #print("paramGrid_nb built")
        paramGrid_ovr = ParamGridBuilder().addGrid(lr.maxIter, [1, 3, 2]).build()
        #print("paramGrid_ovr built")
        paramGrid_rf = ParamGridBuilder().addGrid(rf.numTrees, [2, 3, 1]).build()
        #print("paramGrid_rf built")
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
        
        for i in range(0, len(models_names)):
                crossval_model = CrossValidator(estimator=models[i], estimatorParamMaps=paramGrids[i], evaluator=evaluator, numFolds=numFolds)        
                print("cv Model built: " + models_names[i])
                
                print("Training model: " + models_names[i])
                model = crossval_model.fit(train)
                
                print("Got the best model...")
                best_model = model.bestModel
                
                print(best_model.explainParams())
                best_models.append(best_model)

                print("Predicting model: " + models_names[i])
                preds = model.transform(test)
                preds.select("prediction", "label").show(2)
        
                accuracy = evaluator.evaluate(preds.select("prediction", "label"))
                accuracies.append(accuracy)

                print("Accuracy of " + models_names[i] + " = %g" % accuracy)
                print("=================================\n")
               

        max_accuracy = max(accuracies)
        model_index = accuracies.index(max_accuracy)
        print("index: " + str(model_index))
        print("Using model " + models_names[model_index])
        print("Accuracy %g" % accuracies[model_index])

        print("=================================\n")    
        print("=================================\n")
        print("=================================\n")

        filename = model_dir+models_names[model_index]
        if os.path.exists(filename):
                shutil.rmtree(filename, ignore_errors=True)
        else:
                print("Can not delete the file as it doesn't exists")
        best_models[model_index].save(filename)
        
        if os.path.exists(model_dir+"ovr"):
                if os.path.exists(model_dir+"nb"):
                        shutil.rmtree(model_dir+"nb", ignore_errors=True)
                if os.path.exists(model_dir+"rf"):
                        shutil.rmtree(model_dir+"rf", ignore_errors=True)
        elif os.path.exists(model_dir+"nb"):
                if os.path.exists(model_dir+"ovr"):
                        shutil.rmtree(model_dir+"ovr", ignore_errors=True)
                if os.path.exists(model_dir+"rf"):
                        shutil.rmtree(model_dir+"rf", ignore_errors=True)
        elif os.path.exists(model_dir+"rf"):
                if os.path.exists(model_dir+"ovr"):
                        shutil.rmtree(model_dir+"ovr", ignore_errors=True)
                if os.path.exists(model_dir+"nb"):
                        shutil.rmtree(model_dir+"nb", ignore_errors=True)

        print("Saved model...")
        return models_names[model_index], str(accuracies[model_index])

#train()

