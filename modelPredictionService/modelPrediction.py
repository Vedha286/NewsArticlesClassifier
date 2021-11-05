from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as sf
from pyspark.ml import PipelineModel
import pandas as pd
import numpy as np
from pyspark.ml.classification import NaiveBayesModel, RandomForestClassificationModel, OneVsRestModel
import os
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import re
ps = PorterStemmer()

news_topics = {0: "General News", 1: "Sport", 2: "Tech", 3: "Entertainment", 4: "Finance", 5: "Politics", 6: "Business", 7: "economics", 
               8: "World", 9: "Beauty", 10: "Gaming", 11:"Science", 12:"Travel", 13:"Energy", 14:"Music", 15:"Food"}

r_news_topics = {y: x for x, y in news_topics.items()}


def start_tag(bg):
      	return "<div class='alert alert-" + bg + " alert-dismissible fade show' role='alert'><strong>"

end_tag = "</strong> <button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button></div>"


model_dir = 'models/model-test'

def RemoveNonEnglishWords(text):
        text = str(text)
        text = re.sub('[^a-zA-Z]', ' ', text)
        text = text.lower()
        text = text.split()
        text = [ps.stem(word) for word in text if not word in stopwords.words('english')]
        text = ' '.join(text)
        return text

def predict(sentence):
	sentence = RemoveNonEnglishWords(sentence)
	spark = SparkSession.builder.master("local[0]").appName("newsClassifierPredictor").getOrCreate()

	spark.sparkContext.setLogLevel('WARN')

	print("Article: " + sentence)
	df_test = pd.DataFrame(np.array([["test"]]), columns=['sen'])
	df_test = spark.createDataFrame([(0, sentence)], ["id", "sen"])
#	df_test.show()

	test1 = PipelineModel.load(model_dir+"pipeline").transform(df_test).select("features")
#	test1.show()
	if os.path.exists(model_dir+"ovr"):
		m = OneVsRestModel.load(model_dir+"ovr")
		print("model loaded")
		rr = m.transform(test1)
		pred =  (news_topics[rr.collect()[0]["prediction"]])

		return start_tag("info") + pred + end_tag

	elif os.path.exists(model_dir+"nb"):
		m = NaiveBayesModel.load(model_dir+"nb")
		print("model loaded")
		rr = m.transform(test1)
		pred = (news_topics[rr.collect()[0]["prediction"]])

		return start_tag("info") + pred + end_tag
	elif os.path.exists(model_dir+"rf"):
		m = RandomForestClassificationModel.load(model_dir+"rf")
		print("model loaded")
		rr = m.transform(test1)
		pred =  (news_topics[rr.collect()[0]["prediction"]])

		return start_tag("info") + pred + end_tag
	else:
		pred =  "Error: <span class='font-weight-normal'>There is no model! Please train model again or try again after a while</span>"
		
		return start_tag("danger") + pred + end_tag
	

# y = predict("festivals of India Pictures: festivals of India Photos / Images The country's largest public sector bank, the State Bank of India (SBI) has announced that as part of its festive season scheme, it will be offering credit score linked home loans at 6.7%, irrespective of the loan amount. SBI has also waived processing fees on home loans. Click here to know how to avail SBI home loan.more23 Sep, 2021, 02.10 PM IST21 Sep, 2021, 10.25 AM ISTThe first prototype train of the Kanpur and Agra Metro projects has been inaugurated by Uttar Pradesh Chief Minister Yogi Adi")
# print(y)

# y = predict("air india: Govt begins Air India bid evaluation NEW DELHI: The government has begun evaluation of financial bids received from Tata Group and SpiceJet founder for the acquisition of Air India , sources said.With this, the privatisation process of the national flag carrier has moved to the next phase as the government looks to expeditiously conclude the deal.The financial bids are being evaluated against an undisclosed reserve price and the bid offering the highest price above that benchmark would be accepted.If successful, this will mark the ")
# print(y)


# # entertainment
# y = predict("Country Spotlight: India India is the third-largest emitter of greenhouse gases globally. With a population of almost 1.4 billion people, many of whom are still without access to electricity and clean cooking fuels. In addition, agriculture is the largest source of livelihoods in the country and is the home of the world's second largest cattle population. Consequently, India remains a strong proponent of the Paris Agreement principle of 'common but differentiated responsibilities.'India's Nationally Determined Contribut")
# print(y)

# y = predict("Hrithik Roshan celebrates two years of 'War', says 'Miss everything about being on this set' Miss everything about being on this set - co-working, collaborating, CREATING. #2YearsOfWar @iTIGERSHROFF… https://t.co/0SF5dlxrj3 — Hrithik Roshan (@iHrithik) 1633154487000 Read Also Read Also Siddharth Anand's ‘War', starring Hrithik Roshan and Tiger Shroff completed two glorious years today. Commemorating the occasion, Hrithik took to his Twitter handle to share a poster of the film along with a heartfelt note celebrating the film's success.Along with the poster, he wrote, ‘Miss everything")
# print(y)

# y = predict("20 movie ideas to help put you in the Halloween spirit What would Halloween be without the wonderful witches, ghosts, vampires, and zombies of the big screen? It's no trick that one of the best Halloween treats is sitting down with a big bowl of popcorn to watch your favourite campy flick, family classic, or terrifying horror movie. Here's a list of 20 movie ideas sure to tickle your funny bone or scare you silly. Microsoft and partners may be compensated if you purchase something through recommended links in this article. Microsoft and partners may be compensated if you purchase something through recommended links in this article.")
# print(y)

# y = predict("Charlize Theron prefers impressing kids to critics Country United States of America US Virgin Islands United States Minor Outlying Islands Canada Mexico, United Mexican States Bahamas, Commonwealth of the Cuba, Republic of Dominican Republic Haiti, Republic of Jamaica Afghanistan Albania, People's Socialist Republic of Algeria, People's Democratic Republic of American Samoa Andorra, Principality of Angola, Republic of Anguilla Antarctica (the territory South of 60 deg S) Antigua and Barbuda Argentina, Argentine Republic Armenia Aruba Australia,")
# print(y)

# y = predict("Read Also Choreographer Remo D'Souza and host Raghav Juyal were seen engaging in a fun workout challenge where Raghav tried to woo Shakti Mohan with his quirky style and funny banter with Remo on 'Dance+ 6'.Humorously teasing Raghav for his constant attempts to impress Shakti, Remo initiated a challenge saying: 'Raghav, I have seen you trying to woo Shakti for a few years, but eventually nothing comes out of it and that hurts me since I consider you my own. But then I wondered why should Shakti even consider you; can't put my finger on that one good thing that would impress her.")
# print(y)

# y = predict("John Lennon ‘shattered, totally devastated' by Brian Epstein's death ‘Like a little child' Brian Epstein was the manager of The Beatles from 1962 until his sudden death of an accidental drug overdose in August 1967 at the age of just 32. At the time, John Lennon, Paul McCartney, George Harrison and Ringo Starr had been attending a seminar on Transcendental Meditation in Bangor, Wales, led by Indian guru Maharishi Mahesh Yogi. However, their visit was cut short by the news of Brian's death on August 27.Ajoy Bose, the director of new documentary film The Beatles and India, spoke exclusi")
# print(y)

# #world
# y = predict("India News Video caption: India building collapses hours after it was evacuatedIndia building collapses hours after it was evacuatedNo loss of life was reported from the incident.By Geeta PandeyBBC News, HathrasRajini VaidyanathanBBC South Asia Correspondent By Angie BrownBBC Scotland, Edinburgh and East reporterBy Vikas PandeyBBC News, DelhiBy Soutik BiswasIndia correspondent")
# print(y)

# y = predict("Biden eager to push benefits of spending plan, visiting Michigan Tuesday HOWELL, Mich. — President Joe Biden is shifting strategy to sell his ambitious social spending plans by traveling outside Washington and courting moderate Democrats who are key to hopes for any deal. With his agenda in jeopardy on Capitol Hill, Biden on Tuesday is visiting the Michigan district of a moderate Democratic lawmaker who has urged him to promote his proposals more aggressively to the public. Back in Washington, negotiations continue on a pair of bills to boost spending on safety net, ")
# print(y)


# #food
# y = predict("We all love a good roast on a Sunday but while many of us might think we are dab hands in the kitchen, it's far more enjoyable to get others to do all the cooking - not to mention the washing up afterwards. As we head deeper into autumn, there are few things better than a slap up Sunday lunch in a gastropub or restaurant with a roaring fire, and Bristol is blessed with such places. Below is a round-up of the best roast-serving pubs in Bristol. READ MORE:New bars and restaurants in Bristol to visit this month If we've missed out your favourite, tell us your recommendations in the comments below.")
# print(y)
