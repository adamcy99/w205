# Query Project
- In the Query Project, you will get practice with SQL while learning about Google Cloud Platform (GCP) and BiqQuery. You'll answer business-driven questions using public datasets housed in GCP. To give you experience with different ways to use those datasets, you will use the web UI (BiqQuery) and the command-line tools, and work with them in jupyter notebooks.
- We will be using the Bay Area Bike Share Trips Data (https://cloud.google.com/bigquery/public-data/bay-bike-share). 

#### Problem Statement
- You're a data scientist at Ford GoBike (https://www.fordgobike.com/), the company running Bay Area Bikeshare. You are trying to increase ridership, and you want to offer deals through the mobile app to do so. What deals do you offer though? Currently, your company has three options: a flat price for a single one-way trip, a day pass that allows unlimited 30-minute rides for 24 hours and an annual membership. 

- Through this project, you will answer these questions: 
  * What are the 5 most popular trips that you would call "commuter trips"?
  * What are your recommendations for offers (justify based on your findings)?


## Assignment 02: Querying Data with BigQuery

### What is Google Cloud?
- Read: https://cloud.google.com/docs/overview/

### Get Going

- Go to https://cloud.google.com/bigquery/
- Click on "Try it Free"
- It asks for credit card, but you get $300 free and it does not autorenew after the $300 credit is used, so go ahead (OR CHANGE THIS IF SOME SORT OF OTHER ACCESS INFO)
- Now you will see the console screen. This is where you can manage everything for GCP
- Go to the menus on the left and scroll down to BigQuery
- Now go to https://cloud.google.com/bigquery/public-data/bay-bike-share 
- Scroll down to "Go to Bay Area Bike Share Trips Dataset" (This will open a BQ working page.)


### Some initial queries
Paste your SQL query and answer the question in a sentence.

- What's the size of this dataset? (i.e., how many trips)
  * Answer: There are 983648 rows in the dataset.
  * SQL query:
```sql
#standardSQL
SELECT COUNT(*)
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
```

- What is the earliest start time and latest end time for a trip?
  * Answer: The earlier start time is 2013-08-29 09:08:00.000 UTC and the latest end time for a trip is 2016-08-31 23:48:00.000 UTC
  * SQL query:
```sql
#standardSQL
SELECT MIN(START_DATE), MAX(END_DATE)
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
```

- How many bikes are there?
  * Answer: There are 700 bikes.
  * SQL query:
```sql
#standardSQL
SELECT COUNT(DISTINCT bike_number)
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
```

### Questions of your own
- Make up 3 questions and answer them using the Bay Area Bike Share Trips Data.
- Use the SQL tutorial (https://www.w3schools.com/sql/default.asp) to help you with mechanics.

- Question 1: How many bike users are "Subscribers" and how many are "Customers"?
  * Answer: 136809 bike riders are registered as "Customers" and 846839 are registered as "Subscribers".
  * SQL query:
```sql
#standardSQL
SELECT COUNT(subscriber_type)
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
Where subscriber_type = "Customer"
```
```sql
#standardSQL
SELECT COUNT(subscriber_type)
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
Where subscriber_type = "Subscriber"
```


- Question 2: How many station names are there? How many station ids are there?
  * Answer: There are 84 unique station names and 74 unique station ids. From this, it seems like some station names share the same id.
  * SQL query:
```sql
#standardSQL
SELECT COUNT(distinct start_station_name), COUNT(distinct start_station_id)
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
```


- Question 3: Which station ids have more than 1 station name associated with it?
  * Answer: The station ids: 21, 25, 26, 30, 33, 46, 47, 80, 83, 88 have more than one station name associated with it.
  * SQL query:
```sql
#standardSQL
SELECT start_station_id,
COUNT(distinct start_station_name) AS number_of_station_names
FROM `bigquery-public-data.san_francisco.bikeshare_trips`
GROUP BY start_station_id
HAVING number_of_station_names > 1
ORDER BY start_station_id
```


