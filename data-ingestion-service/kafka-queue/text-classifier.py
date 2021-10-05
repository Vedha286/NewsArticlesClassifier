from pymongo import MongoClient

import string
import spacy
import numpy as np
from sklearn.neighbors import NearestNeighbors

label_names = ['business', 'entertainment', 'politics', 'sport', 'tech']

docs = ["UK economy facing 'major risks'",
"The UK manufacturing sector will continue to face 'serious challenges' over the next two years, the British Chamber of Commerce (BCC) has said.",
"The group's quarterly survey of companies found exports had picked up in the last three months of 2004 to their best levels in eight years. The rise came despite exchange rates being cited as a major concern. However, the BCC found the whole UK economy still faced 'major risks' and warned that growth is set to slow. It recently forecast economic growth will slow from more than 3% in 2004 to a little below 2.5% in both 2005 and 2006.",
"Manufacturers' domestic sales growth fell back slightly in the quarter, the survey of 5,196 firms found. Employment in manufacturing also fell and job expectations were at their lowest level for a year.",
"Despite some positive news for the export sector, there are worrying signs for manufacturing,' the BCC said. 'These results reinforce our concern over the sector's persistent inability to sustain recovery.' The outlook for the service sector was 'uncertain' despite an increase in exports and orders over the quarter, the BCC noted.",
"The BCC found confidence increased in the quarter across both the manufacturing and service sectors although overall it failed to reach the levels at the start of 2004. The reduced threat of interest rate increases had contributed to improved confidence, it said. The Bank of England raised interest rates five times between November 2003 and August last year. But rates have been kept on hold since then amid signs of falling consumer confidence and a slowdown in output. 'The pressure on costs and margins, the relentless increase in regulations, and the threat of higher taxes remain serious problems,' BCC director general David Frost said. 'While consumer spending is set to decelerate significantly over the next 12-18 months, it is unlikely that investment and exports will rise sufficiently strongly to pick up the slack."
]

docs = []
true_preds = []
client = MongoClient("mongodb+srv://IIITH-group10:LeoEXtI5sxntXmpG@cluster0.jejzt.mongodb.net/news?retryWrites=true&w=majority")

myresult = client.news.newsArticles.find({ "category": "news" })
for x in myresult:
      try:
            if(x["summary"]):
                  docs.append(x["summary"])
      except Exception as e: 
            print("Exception : " + str(e))      

client.close()

def clean_text(text: string):
      try:
            text = text.translate(str.maketrans('', '', string.punctuation))
            text = text.lower()
            text = text.replace('\n', ' ')
            text = ' '.join(text.split())  # remove multiple whitespaces
      except Exception as e: 
            print("Exception : " + str(e))
            print("Test : " + str(text))

      return text
      

def embed(tokens, nlp):
      """Return the centroid of the embeddings for the given tokens.

      Out-of-vocabulary tokens are cast aside. Stop words are also
      discarded. An array of 0s is returned if none of the tokens
      are valid.

      """

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

nlp = spacy.load('en_core_web_lg')     


      
label_vectors = np.asarray([
      embed(label.split(' '), nlp)
      for label in label_names
])
# print(label_vectors)
# print("=================================")
k = int(len(docs)/len(label_names))
print(len(docs))
print(k)
neigh = NearestNeighbors(n_neighbors=len(label_names))
neigh.fit(label_vectors)

def predict(doc, nlp, neigh):
      doc = clean_text(doc)
      tokens = doc.split(' ')[:50]
      centroid = embed(tokens, nlp)
      closest_label = neigh.kneighbors([centroid], return_distance=False)[0][0]
      return closest_label

preds = [label_names[predict(doc, nlp, neigh)] for doc in docs]
# print(preds)
for i in range(len(preds)):
      print(preds[i] + " : " + docs[i])
      print("=========================================")

