from pymongo import MongoClient, errors
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext   
from pyspark.ml import Pipeline

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
import pickle


mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"
spark = SparkSession.builder.appName("newsClassifier").getOrCreate()


def get_data():
	try:
		client = MongoClient(mongodb_connection_string)
		db = client.news
		print('Getting data')
		newsArticles = db.newsArticles.find({}, {"_id":0, "date":0, "source":0})
		client.close() 

		newsArticlesArr = []
		for newsArticle in newsArticles:
			newsArticlesArr.append(newsArticle)

		print('Got ' + str(len(newsArticlesArr)) + ' records\n')

		df = spark.createDataFrame(newsArticlesArr)

		rddX = df.rdd.map(lambda x: str(x['title']) + ' ' + str(x['summary']))

		X = rddX.collect() # Vectorize(rddX.collect())
		print('Vectorized X data shape:')
		print(X.shape)

		Y = df.rdd.map(lambda x: str(x['category']))
		print('\nY data shape (showing top 5):')
		print(Y.collect()[:5])

		return X, Y
	except errors as e:
		print("Error getting data " + str(e))
		return null    

corpus, true_preds = get_data()



X_train, X_test, y_train, y_test = train_test_split(corpus, true_preds, test_size=0.3)
tfidf = TfidfVectorizer(ngram_range=(1, 3), stop_words='english')

MultinomialNB_model = make_pipeline(tfidf, MultinomialNB(alpha=5))
svm_linear_model = make_pipeline(tfidf, SVC(kernel = 'linear',gamma=1, C = 1.2))
svm_model_rbf_model = make_pipeline(tfidf, SVC(kernel = 'rbf',gamma=1, C = 1))
svm_model_sigmoid_model = make_pipeline(tfidf, SVC(kernel='sigmoid', gamma=1, C=1.5))
svm_model_poly_model = make_pipeline(tfidf, SVC(kernel='poly', degree=3, C=3))
RandomForestClassifier_model = make_pipeline(TfidfVectorizer(), RandomForestClassifier())


models = [
      MultinomialNB_model, 
      svm_linear_model, 
      svm_model_rbf_model, 
      svm_model_sigmoid_model, 
      svm_model_poly_model,
      RandomForestClassifier_model
]

models_names = [
      "MultinomialNB",
      "svm linear",
      "svm rbf",
      "svm sigmoid",
      "svm poly",
      "Random Forest"
]

accuracies = []

for i in range(0, 1):
      print("Training model: " + models_names[i])
      models[i].fit(X_train,  y_train)
      
      print("Predicting model: " + models_names[i])
      preds = models[i].predict(X_test)
            
      print("Finding accuracy of model: " + models_names[i])
      accuracy = accuracy_score(y_test, preds)
      accuracies.append(accuracy)
      print(models_names[i] +" Classifier trained with accuracy: " + str(accuracy))
      print("=================================\n")


max_accuracy = max(accuracies)
model_index = accuracies.index(max_accuracy)
print("index: " + str(model_index))
news_model_file = "../models/news_nb.pkl"
pickle.dump(models[model_index], open(news_model_file, "wb"))

print("saved model")
