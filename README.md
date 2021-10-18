# NewsArticlesClassifier

#### Hack Elite(Group 10) - **Vedha Krishna Velthapu and P Manish**

## Problem Statement

https://github.com/Vedha286/NewsArticlesClassifier/blob/main/documents/IIIT%20H%20Capstone%20Project%20-%20News%20articles%20classifier.pdf

## Planning Document

https://docs.google.com/document/d/12yBr9iS_2Y7TUdLg-8Pu-fC3epiNBLcLnXRKi2ezRB4/edit?usp=sharing

# Milestone 2- Model Training (cleaning + preprocessing of data)

#### `milestone2` branch

## Report

1.  Environment details:

    - Database: Free MongoDB database on cloud
    - Data processing: PySpark 

2.  What goes in as an input:

    The data from our database what we collected from milestone 1.

3.  How the input is being processed:

- We first fetched all the data from ou databse using pymongo and created a spark dataframe with that data.
- To clean the X values:
    - We concatinated the title and summary and removed all the non english words, spaces and spacial characters from the text. We used nltk and stopwords for this.
    - Lastly we converted an array of the cleaned texts into a matrix of token counts which can be passed as input to our model. We used sklearn's CountVectorizer (sklearn.feature_extraction.text.CountVectorizer) to do this, the paramaeter for the CountVectorizer is `max_features = 5000` and `ngram_range = (1,3)`. 
- To clean the Y values:
    - The Y values we already cleaned and validated before inserting into the database as we knew this was an important value.


4.  What comes out as an output:

   The output is a matrix of token counts as the X values and a list of categories as the Y values. These values can directly be passed into the model we have in mind as inputs.

5.  Challenges encountered and the way you tackled them:

    **Problem 1:**

         Getting data from our mongodb database using pyspark

         Solution: Our mentor showed us a few examples which helped us get around the issue. Instead of fetching data using pyspark, we got data using pymongo and created a spark dataframe with that data to process it.

    **Problem 2:**

         Find an appropriate model for our problem, as we wanted to process our data to work for that specific model

         Solution: We could not find an example of a text classifier model that accepts title, summary and date of the news article as a input, all the models just took in 1 string as input. Based on this we also decided to not pass in date as an input to train the model, and we contatinated the title and summary to form 1 string.


## Running Instructions

1.  Create a fork of the repo using the `fork` button.
2.  Clone your fork using git clone `https://github.com/Vedha286/NewsArticlesClassifier.git`
3.  Change to `milestone2` branch.
4.  To setup kafka follow the steps https://github.com/Vedha286/NewsArticlesClassifier/blob/milestone2/model-training-service/setup-steps
5.  Change directory: `cd model-training-service`
8.  Install dependencies using: `pip3 install -r requirements.txt`
9.  Run code: `python3 get_data.py`



# Milestone 1- Data Ingestion

#### `milestone1` branch

## Architectural Design

https://github.com/Vedha286/NewsArticlesClassifier/blob/milestone1/documents/architectural-design.png

## Planning Document

https://docs.google.com/document/d/12yBr9iS_2Y7TUdLg-8Pu-fC3epiNBLcLnXRKi2ezRB4/edit?usp=sharing

**Note: The table in the document shows exactly what is implemented and what was completed, as well as who was incharge of what task.**

## Report

1.  Environment details:

    - Database: Free MongoDB database on cloud
    - Streaming: Apache Kafka

2.  What goes in as an input:

    The data we get from our APIs is our input for this milestone. We made use of the `free news api` (https://rapidapi.com/newscatcher-api-newscatcher-api-default/api/free-news/) and the `newscatcher api` (https://newscatcherapi.com/).

3.  How the input is being processed:

- We validate that all the fields we needs is in returned by the API (`published-date`,`topic/category`,`title`,`summary`, and `source`).
- Both the APIs we used had a `news` category which we changed to `general news` before the article is stored in the database to reduce some ambiguity.
- The topic we used in kafka is `news-train`

4.  What comes out as an output:

    Strutured data stored in our database with the following columns:

    - **title**: Which is the title of the news article
    - **summary**: Which is the news article summary
    - **category**: The category the news belongs to, i.e sports, health
    - **source**: URL link to the original news article
    - **date**: Date the news article was published

Screenshot of data collected so far:
![image](https://user-images.githubusercontent.com/55736158/136701394-bbc78876-aa6c-4bbe-9549-a4c281b34201.png)

![image](https://user-images.githubusercontent.com/55736158/136701432-84817412-4b0c-48a9-b602-f85668a6ee6c.png)

5.  Challenges encountered and the way you tackled them:

    **Problem 1:**

         Lack of understanding on Kafka and kafka queues

         Solution: Spliting the task so 1 person focus solely on Kafka until it is set up, instead of 2 people working on it together helped us. We managed to finish the other tasks along with Kafka in time.

    **Problem 2:**

         Not saving duplicates on MongoDB and both the team members are not very experienced with MongoDB

         Solution: We managed to created a unique index on the title, so any article with repeating titles will fail to save.

    **Problem 3:**

         Saving large amounts of documets to the database was taking long and with bulk insert, if a document fails all documents after that won't save. With the unique title constraint if the a document failed all the documents after that won't save

         Solution: We decided to insert all the docuemnts individually in a try-catch block. If there are any exceptions while saving the documents, it will not stop the application from running. Even though this is a bit slower, we would rather have a slow write than a lot of documents failing to save to the database.

    **Problem 4:**

         Coordinating and working together between different time zones

         Solution: Communicating reqularly and meeting every 2-3 days to have alignment on our tasks.

    **Problem 5:**

         Finding a good source to get news articles from as most of the sources/apis were paid

         Solution: After a lot of research we found 1 api we can use and the free news api provided, worked for us.

## Running Instructions

1.  Create a fork of the repo using the `fork` button.
2.  Clone your fork using git clone `https://github.com/Vedha286/NewsArticlesClassifier.git`
3.  Change to `milestone1` branch.
4.  To setup kafka follow the steps https://github.com/Vedha286/NewsArticlesClassifier/edit/milestone1/data-ingestion-service/setup-steps
5.  On terminal 1 run: `./kafka_2.12-3.0.0/bin/zookeeper-server-start.sh ./kafka_2.12-3.0.0/config/zookeeper.properties`
6.  On terminal 2 run: `./kafka_2.12-3.0.0/bin/kafka-server-start.sh ./kafka_2.12-3.0.0/config/server.properties`
7.  On terminal 3 run: `cd data-ingestion-service`
8.  Install dependencies using: `pip3 install -r requirements.txt`
9.  On terminal 3 run: `python3 consumer.py`
10. On terminal 4 run: `python3 producer.py`
