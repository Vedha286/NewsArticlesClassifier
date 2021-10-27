import pandas as pd
import nltk
import re
from scipy import spatial
import matplotlib.pyplot as plt
from pymongo import MongoClient, errors

import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
from sklearn.neighbors import NearestNeighbors
from sklearn.svm import SVC

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

import numpy as np
import en_core_web_lg

nlp = en_core_web_lg.load()

news_topics = {0: "general news", 1: "sport", 2: "tech", 3: "entertainment", 4: "finance", 5: "politics", 6: "business", 7: "economics", 
               8: "world", 9: "beauty", 10: "gaming", 11:"science", 12:"travel", 13:"energy", 14:"music", 15:"food"}

r_news_topics = {y: x for x, y in news_topics.items()}

label_names = list(news_topics.values())

label_names.remove("general news")
label_names.remove("music")
label_names.remove("travel")
label_names.remove("energy")

ps = PorterStemmer()


def remove_non_english_words(word):
      review = re.sub('[^a-zA-Z0-9]', ' ', word)
      review = review.lower()
      review = review.split()

      review = [ps.stem(word) for word in review if not word in stopwords.words('english')]
      review = ' '.join(review)
      return review

def embed(tokens, nlp):
      
      lexemes = (nlp.vocab[token] for token in tokens)

      vectors = np.asarray([
            lexeme.vector
            for lexeme in lexemes
            if lexeme.has_vector
            and not lexeme.is_stop
            and len(lexeme.text) > 1
      ])
      if len(vectors) > 0:
            centroid = vectors.mean(axis=0)
      else:
            width = nlp.meta['vectors']['width']  # typically 300
            centroid = np.zeros(width)

      return centroid

def predict(doc, nlp, neigh):
      doc = remove_non_english_words(doc)
      tokens = doc.split(' ')
      centroid = embed(tokens, nlp)
      closest_label = neigh.kneighbors([centroid], return_distance=False)[0][0]
      return closest_label

mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"

client = MongoClient(mongodb_connection_string)
db = client.news
print('Getting data')
newsArticles = db.newsArticles.find({}, {"_id":0, "date":0, "source":0})
client.close() 

# df = pd.read_csv("E:/IIITH/capstone project/data.csv") 

newsArticlesArr = []
# for i in range(0, len(df)):
for newsArticle in newsArticles:
      # newsArticlesArr.append({"title": df["title"][i], "summary": df["summary"][i], "category": df["category"][i]})
      newsArticlesArr.append(newsArticle)

print(len(newsArticlesArr))

 
label_vectors = np.asarray([
      embed([label], nlp)
      for label in  label_names
])
print(label_vectors)
print("=================================")


corpus=[]
true_preds = []

for i in range(0, len(newsArticlesArr)):
      text = str(newsArticlesArr[i]['title']) + ' ' + str(newsArticlesArr[i]['summary'] )
      true_preds.append(str(newsArticlesArr[i]['category']))
      corpus.append(remove_non_english_words(text))
      if i % 100 == 0:
            print('i: ' + str(i))

print("corpus len: " + str(len(corpus)))
print("=================================")


neigh = NearestNeighbors(n_neighbors=7, metric=spatial.distance.cosine, p=1)
neigh.fit(label_vectors)
print("Geting y values")
print("=================================")


y=[]
for i in range(0, len(corpus)):
      if(true_preds[i] != 'general news' and true_preds[i] != 'music' and true_preds[i] != 'energy' and true_preds[i] != 'travel'):
            y_label = true_preds[i]
      else:
            y_label = label_names[predict(corpus[i], nlp, neigh)]
            
      y.append(y_label)
      if i % 100 == 0:
            print('i: ' + str(i))

preds_count = [y.count(label) for label in label_names]

print(preds_count)
print("=================================")


fig = plt.figure(figsize = (20, 5))
 
# creating the bar plot
plt.bar(label_names, preds_count, color ='blue', width = 0.4)
 
plt.xlabel("Topics")
plt.ylabel("No. of news")
plt.title("News for different topics")
plt.show()


y = [r_news_topics[d] for d in y]
X_train, X_test, y_train, y_test = train_test_split(corpus, y, test_size=0.3)

MultinomialNB_model = make_pipeline(TfidfVectorizer(), MultinomialNB(alpha=5))
MultinomialNB_model.fit(X_train,  y_train)
MultinomialNB_preds = MultinomialNB_model.predict(X_test)
MultinomialNB_acc = accuracy_score(y_test, MultinomialNB_preds)
    
print(f"MultinomialNB Classifier trained with accuracy: " + str(MultinomialNB_acc))

svm_linear_model = make_pipeline(TfidfVectorizer(), SVC(kernel = 'linear',gamma=0.5, C = 1.2))
svm_linear_model.fit(X_train, y_train)
svm_predictions_linear = svm_linear_model.predict(X_test)
svm_model_linear_acc = accuracy_score(y_test, svm_predictions_linear)
    
print(f"svm linear Classifier trained with accuracy: " + str(svm_model_linear_acc))

svm_model_rbf_model = make_pipeline(TfidfVectorizer(), SVC(kernel = 'rbf',gamma=0.5, C = 1.2))
svm_model_rbf_model.fit(X_train, y_train)
svm_predictions_rbf = svm_model_rbf_model.predict(X_test)
svm_model_rbf_acc = accuracy_score(y_test, svm_predictions_rbf)
    
print(f"svm rbf Classifier trained with accuracy: " + str(svm_model_rbf_acc))

svm_model_sigmoid_model = make_pipeline(TfidfVectorizer(), SVC(kernel='sigmoid', gamma=0.5, C=1.5))
svm_model_sigmoid_model.fit(X_train, y_train)
svm_predictions_sigmoid = svm_model_sigmoid_model.predict(X_test)
svm_model_sigmoid_acc = accuracy_score(y_test, svm_predictions_sigmoid)
    
print(f"svm sigmoid Classifier trained with accuracy: " + str(svm_model_sigmoid_acc))

svm_model_poly_model = make_pipeline(TfidfVectorizer(), SVC(kernel='poly', degree=3, C=3))
svm_model_poly_model.fit(X_train, y_train)
svm_predictions_poly = svm_model_poly_model.predict(X_test)
svm_model_poly_acc = accuracy_score(y_test, svm_predictions_poly)
    
print(f"svm poly Classifier trained with accuracy: " + str(svm_model_poly_acc))


news_model_file = "E:/IIITH/capstone project/NewsArticlesClassifier/model-training-service/models/news_nb.pkl"

if(MultinomialNB_acc >= svm_model_linear_acc and MultinomialNB_acc >= svm_model_sigmoid_acc and MultinomialNB_acc >= svm_model_rbf_acc and MultinomialNB_acc >= svm_model_poly_acc):
      pickle.dump(MultinomialNB_model, open(news_model_file, "wb"))

elif(svm_model_linear_acc >= MultinomialNB_acc and svm_model_linear_acc >= svm_model_sigmoid_acc and svm_model_linear_acc >= svm_model_rbf_acc and svm_model_linear_acc >= svm_model_poly_acc):
      pickle.dump(svm_linear_model, open(news_model_file, "wb"))

elif(svm_model_rbf_acc >= MultinomialNB_acc and svm_model_rbf_acc >= svm_model_linear_acc and svm_model_rbf_acc >= svm_model_sigmoid_acc and svm_model_rbf_acc >= svm_model_poly_acc):
      pickle.dump(svm_model_rbf_model, open(news_model_file, "wb"))

elif(svm_model_sigmoid_acc >= MultinomialNB_acc and svm_model_sigmoid_acc >= svm_model_linear_acc and svm_model_sigmoid_acc >= svm_model_rbf_acc and svm_model_sigmoid_acc >= svm_model_poly_acc):
      pickle.dump(svm_model_sigmoid_model, open(news_model_file, "wb"))

else:
      pickle.dump(svm_model_poly_model, open(news_model_file, "wb"))