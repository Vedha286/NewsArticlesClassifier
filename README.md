# NewsArticlesClassifier

#### Hack Elite - **Vedha Krishna Velthapu and P Manish**

## Problem Statement

https://github.com/Vedha286/NewsArticlesClassifier/blob/main/documents/IIIT%20H%20Capstone%20Project%20-%20News%20articles%20classifier.pdf

# Week 1- Data Ingestion

## Architectural Design

https://github.com/Vedha286/NewsArticlesClassifier/blob/milestone1/documents/architectural-design.png

## Planning Document

https://docs.google.com/document/d/12yBr9iS_2Y7TUdLg-8Pu-fC3epiNBLcLnXRKi2ezRB4/edit?usp=sharing
**Note: The table in the document shows exactly what is implemented and what was completed, as well as who was incharge of what task.**

## Report

1. Environment details:

   - Database: Free MongoDB atlas could database
   - Streaming: Apache Kafka

2. What goes in as an input:

   The data we get from our APIs is our input for this milestone. We made use of the `free news api` (https://rapidapi.com/newscatcher-api-newscatcher-api-default/api/free-news/) and the `newscatcher api` (https://newscatcherapi.com/).

3. How the input is being processed:

   - We validate that all the fields we needs is in returned by the API (`published-date`,`topic/category`,`title`,`summary`, and `source`).
   - Both the APIs we used had a `news` category which we changed to `general news` before the article is stored in the database to reduce some ambiguity.

4. What comes out as an output:

   Strutured data stored in our database with the following columns:

   - **title**: Which is the title of the news article
   - **summary**: Which is the news article summary
   - **category**: The category the news belongs to, i.e sports, health
   - **source**: URL link to the original news article
   - **date**: Date the news article was published

   Screenshot of data collected so far:
   ![image](https://user-images.githubusercontent.com/55736158/136675390-2f918e53-59fb-43f8-a094-07934c14d4fb.png)

   ![image](https://user-images.githubusercontent.com/55736158/136675367-139481b2-60f3-4a75-abd6-2b13b9fb008f.png)

5. Challenges encountered and the way you tackled them:

   **Problem 1:** Lack of understanding on Kafka and kafka queues
   **Solution:** Spliting the task so 1 person focus solely on Kafka until it is set up, instead of 2 people working on it together helped us. We managed to finish the other tasks alone with Kafka


   **Problem 2:** Not saving duplicates on MongoDB and both the team members are noobs with MongoDB
   **Solution:** We managed to created a unique index on the title, so any article with repating titles will fail.


   **Problem 3:** Saving large amounts of documets to the database was taking long and with bulk insert if a document fails all documents after that won't save. With the unique containrt on the title if the a document failed all the documents after that won't save
   **Solution:** We decided to insert all the docuemnts individually in a try catch block to any exception while saving the dcumets will not stop the application from running. Even though this is slower we rather have a slow write than a lot of documents failing to save to the database.

   
   **Problem 4:** Coordinating and working together between different time zones
   **Solution:** Communicating reqularly and meeting every 2-3 days to have alignment on our tasks.

   
   **Problem 5:** Find a good source to get data from as most of the sources were paid
   **Solution:** After a lot of research we found 1 api we can use and the free news api provided worked for us.
