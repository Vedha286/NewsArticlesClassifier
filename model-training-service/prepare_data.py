import pandas as pd
import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import re
from sklearn.feature_extraction.text import CountVectorizer
ps = PorterStemmer()
cv = CountVectorizer(max_features = 5000, ngram_range = (1,3))	

def RemoveNonEnglishWords(text):
	text = re.sub('[^a-zA-Z]', '', text)
	text = text.lower()
	text = text.split()

	text = [ps.stem(word) for word in text if not word in stopwords.words('english')]
	text = ''.join(text)
	return text

def Vectorize(words):	
	return cv.fit_transform(words).toarray()
