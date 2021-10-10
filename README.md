# NewsArticlesClassifier

#### Group 10 - **Vedha Krishna Velthapu and P Manish**

### Problem Statement:
https://github.com/Vedha286/NewsArticlesClassifier/blob/main/documents/IIIT%20H%20Capstone%20Project%20-%20News%20articles%20classifier.pdf


# Week 1- Data Ingestion

## Architectural Design
https://github.com/Vedha286/NewsArticlesClassifier/blob/week1/documents/architectural-design.png

## Planning Document:
https://docs.google.com/document/d/12yBr9iS_2Y7TUdLg-8Pu-fC3epiNBLcLnXRKi2ezRB4/edit?usp=sharing

## Report

1. Environment details
   - Database: We made use of the free ongodb atlas could database
   - Streaming: Apache Kafka
2. What goes in as an input
   The data we get from our APIs is our input for this milestone. We made use of the free news api and the newscather api. Since it is impossible to get every possible news articles, we get the daily top 5 trending keywords on google using the google trends api service, for the query keywords to make the API calls. This was done so we don't have to hard code the keywords and also get the most relavent keywords to get news on.
3. How the input is being processed
   - We validate that all the fields we needs is in returned by the API (`published-date`,`topic/category`,`title`,`summary`, and `source`).
   - Both the APIs we used had a `news` category which we changed to `general news` before the article is stored in the database to reduce some ambiguity.
4. What comes out as an output

   Strutured data stored in our database with the following columns:

   - **title**: Which is the title of the news article
   - **summary**: Which is the news article summary
   - **category**: The category the news belongs to, i.e sports, health
   - **source**: URL link to the original news article
   - **date**: Date the news article was published

   Screenshot of data collected so far:
   ![image](https://user-images.githubusercontent.com/55736158/136675390-2f918e53-59fb-43f8-a094-07934c14d4fb.png)
   
   ![image](https://user-images.githubusercontent.com/55736158/136675367-139481b2-60f3-4a75-abd6-2b13b9fb008f.png)

5. Challenges encountered and the way you tackled them
   - Lack of understanding on Kafka
   - Coordinating and working together between different time zones
   - Find a good source to get data from as most of the sources were paid
