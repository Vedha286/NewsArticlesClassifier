import re
from pymongo import MongoClient, errors

import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

news_topics = {0: "general news", 1: "sport", 2: "tech", 3: "entertainment", 4: "finance", 5: "politics", 6: "business", 7: "economics", 
               8: "world", 9: "beauty", 10: "gaming", 11:"science", 12:"travel", 13:"energy", 14:"music", 15:"food"}

r_news_topics = {y: x for x, y in news_topics.items()}

ps = PorterStemmer()

def remove_non_english_words(word):
      review = re.sub('[^a-zA-Z0-9]', ' ', word)
      review = review.lower()
      review = review.split()

      review = [ps.stem(word) for word in review if not word in stopwords.words('english')]
      review = ' '.join(review)
      return review

mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"

client = MongoClient(mongodb_connection_string)
db = client.news
print('Getting data')
newsArticles = db.newsArticles.find({}, {"_id":0, "date":0, "source":0})
client.close() 

newsArticlesArr = []
for newsArticle in newsArticles:
      newsArticlesArr.append(newsArticle)

print(len(newsArticlesArr))


corpus=[]
true_preds = []

for i in range(0, len(newsArticlesArr)):
      text = str(newsArticlesArr[i]['title']) + ' ' + str(newsArticlesArr[i]['summary'] )
      true_preds.append(str(newsArticlesArr[i]['category']))
      # corpus.append(remove_non_english_words(text))
      corpus.append(text)
      if i % 100 == 0:
            print('i: ' + str(i))

print("corpus len: " + str(len(corpus)))
print("=================================")


y=true_preds

print("=================================")

y = [r_news_topics[d] for d in y]
X_train, X_test, y_train, y_test = train_test_split(corpus, y, test_size=0.3)
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')
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
model_train_data = []

for i in range(0, 2):
      
      kf = KFold(n_splits=4, shuffle=True)
      print("Training model: " + models_names[i])
      model_accuracies = []
      kf_model_train_data = {}
      for train_index, test_index in kf.split(corpus):
            print("TRAIN:", train_index, "TEST:", test_index)
            X_train = [corpus[i] for i in train_index]
            y_train = [y[i] for i in train_index]
            X_test = [corpus[i] for i in test_index]
            y_test = [y[i] for i in test_index]
            models[i].fit(X_train,  y_train)
            print("Predicting model: " + models_names[i])
            preds = models[i].predict(X_test)
            print("Finding accuracy of model: " + models_names[i])
            accuracy = accuracy_score(y_test, preds)
            if(len(model_accuracies)> 0):
                  if(accuracy >= max(model_accuracies)):
                        kf_model_train_data = X_train, y_train
            else:
                  kf_model_train_data = X_train, y_train
            model_accuracies.append(accuracy)
            print(models_names[i] +" Classifier trained with accuracy: " + str(accuracy) + "\n")

      print("=================================\n")
      accuracies.append(model_accuracies)
      model_train_data.append(kf_model_train_data)
      
            
      
# for i in range(0, len(models)):
#       print("Training model: " + models_names[i])
#       models[i].fit(X_train,  y_train)
      
#       print("Predicting model: " + models_names[i])
#       preds = models[i].predict(X_test)
            
#       print("Finding accuracy of model: " + models_names[i])
#       accuracy = accuracy_score(y_test, preds)
#       accuracies.append(accuracy)
#       print(models_names[i] +" Classifier trained with accuracy: " + str(accuracy))
#       print("=================================\n")


max_accuracy = max(accuracies)
model_index = accuracies.index(max_accuracy)
models[model_index].fit(model_train_data[model_index][0], model_train_data[model_index][1])

news_model_file = "E:/IIITH/capstone project/NewsArticlesClassifier/model-training-service/models/news_nb.pkl"
pickle.dump(models[model_index], open(news_model_file, "wb"))