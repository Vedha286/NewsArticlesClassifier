
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from pymongo import MongoClient, errors
from sklearn.model_selection import train_test_split

from scipy import spatial

news_topics = {0: "general news", 1: "sport", 2: "tech", 3: "entertainment", 4: "finance", 5: "politics", 6: "business", 7: "economics", 
               8: "world", 9: "beauty", 10: "gaming", 11:"science", 12:"travel", 13:"energy", 14:"music", 15:"food"}

r_news_topics = {y: x for x, y in news_topics.items()}

label_names = list(news_topics.values())

label_names.remove("general news")
label_names.remove("music")
label_names.remove("travel")
label_names.remove("energy")

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

corpus = []
true_preds = []
corpus1 = []
true_preds1 = []

for i in range(0, len(newsArticlesArr)):
      category = str(newsArticlesArr[i]['category'])
      text = str(newsArticlesArr[i]['title']) + ' ' + str(newsArticlesArr[i]['summary'] )       

      if(category != 'general news' and category != 'music' and category != 'energy' and category != 'travel'):
            true_preds.append(category)
            corpus.append((text))
      else:
            true_preds1.append(category)
            corpus1.append((text))
      if i % 100 == 0:
            print('i: ' + str(i))

print("corpus len: " + str(len(corpus)))
print("corpus(general) len: " + str(len(corpus1)))
print("=================================")
knn = KNeighborsClassifier(n_neighbors=12, metric=spatial.distance.cosine)

text_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', knn),
])
# Fitting our train data to the pipeline
X_train, X_test, y_train, y_test = train_test_split(corpus, true_preds, test_size=0.3)
text_clf.fit(X_train, y_train)
print(type(X_test))
#predicted = text_clf.predict(X_test)
#print('We got an accuracy of',np.mean(predicted == y_test)*100, '% over the test data.')


print("Geting y values")
print("=================================")


# y = true_preds
# for i in range(0, len(corpus1)):
#       #if(true_preds[i] != 'general news' and true_preds[i] != 'music' and true_preds[i] != 'energy' and true_preds[i] != 'travel'):
#       #      y_label = true_preds[i]
#       #else:
#       y_label = text_clf.predict([corpus[i]])[0]
            
#       y.append(y_label)
#       if i % 100 == 0:
#             print('i: ' + str(i))
# print(len(y))

# preds_count = [y.count(label) for label in label_names]

# print(preds_count)
# print("=================================")
# import matplotlib.pyplot as plt
# fig = plt.figure(figsize = (20, 5))
 
# # creating the bar plot
# plt.bar(label_names, preds_count, color ='blue', width = 0.4)
 
# plt.xlabel("Topics")
# plt.ylabel("No. of news")
# plt.title("News for different topics")
# plt.show()