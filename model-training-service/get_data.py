from pymongo import MongoClient, errors

mongodb_connection_string = "mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority"

client = MongoClient(mongodb_connection_string)
db = client.news
newsArticles = db.newsArticles.find({})
newsArticlesArr = []
for newsArticle in newsArticles:
	#print(newsArticle)
	newsArticlesArr.append(newsArticle)

print(newsArticlesArr)  # data is in array -> can convert to a dataframe    pd.Dataframe(newsArticlesArr)

print(len(newsArticlesArr))
