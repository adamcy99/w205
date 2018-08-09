
# Query Project
- In the Query Project, you will get practice with SQL while learning about Google Cloud Platform (GCP) and BiqQuery. You'll answer business-driven questions using public datasets housed in GCP. To give you experience with different ways to use those datasets, you will use the web UI (BiqQuery) and the command-line tools, and work with them in jupyter notebooks.
- We will be using the Bay Area Bike Share Trips Data (https://cloud.google.com/bigquery/public-data/bay-bike-share). 

#### Query Project Problem Statement
- You're a data scientist at Ford GoBike (https://www.fordgobike.com/), the company running Bay Area Bikeshare. You are trying to increase ridership, and you want to offer deals through the mobile app to do so. What deals do you offer though? Currently, your company has three options: a flat price for a single one-way trip, a day pass that allows unlimited 30-minute rides for 24 hours and an annual membership. 

- Through this project, you will answer these questions: 
  * What are the 5 most popular trips that you would call "commuter trips"?
  * What are your recommendations for offers (justify based on your findings)?

_______________________________________________________________________________________________________________


## Assignment 04 - Querying data - Answer Your Project Questions

### Your Project Questions

- Answer at least 4 of the questions you identified last week.
- You can use either BigQuery or the bq command line tool.
- Paste your questions, queries and answers below.

- Question 1: How many trips can be called "commuter trips" going to work? Lets assume that a "commuter trip" going to work occurs between 6am - 10am from Monday to Friday (following MTA train rules).  
  * Answer: There are 305724 morning "commuter trips". (Note: SQL starts counting day of week from Sunday so 1 = Sunday).
  * SQL query:

    ```
    bq query --use_legacy_sql=false '
        SELECT COUNT(start_date)
        FROM `bigquery-public-data.san_francisco.bikeshare_trips`
        WHERE EXTRACT(DAYOFWEEK FROM start_date) > 1
        AND EXTRACT(DAYOFWEEK FROM start_date) <= 6
        AND EXTRACT(TIME FROM start_date) >= "06:00:00.000"
        AND EXTRACT(TIME FROM start_date) <= "10:00:00.000"'
    ```

- Question 2: How many trips can be called "commuter trips" returning from work? Lets assume that a "commuter trip" returning from work occurs between 4pm - 8pm from Monday to Friday (following MTA train rules).
  * Answer: There are 312483 evening "commuter trips".
  * SQL query:

    ```
    bq query --use_legacy_sql=false '
        SELECT COUNT(start_date) 
        FROM `bigquery-public-data.san_francisco.bikeshare_trips` 
        WHERE EXTRACT(DAYOFWEEK FROM start_date) > 1 
        AND EXTRACT(DAYOFWEEK FROM start_date) <= 6 
        AND EXTRACT(TIME FROM start_date) >= "16:00:00.000" 
        AND EXTRACT(TIME FROM start_date) <= "20:00:00.000"'
    ```

- Question 3: How many "commuter trips" are 30 minutes and less? 
  * Answer: There are 607903 "commuter trips" that are 30 minutes and less.
  * SQL query:

    ```
    bq query --use_legacy_sql=false '
        SELECT COUNT(start_date)
        FROM `bigquery-public-data.san_francisco.bikeshare_trips`
        WHERE (EXTRACT(DAYOFWEEK FROM start_date) > 1
        AND EXTRACT(DAYOFWEEK FROM start_date) <= 6)
        AND ((EXTRACT(TIME FROM start_date) >= "06:00:00.000"
        AND EXTRACT(TIME FROM start_date) <= "10:00:00.000")
        OR (EXTRACT(TIME FROM start_date) >= "16:00:00.000"
        AND EXTRACT(TIME FROM start_date) <= "20:00:00.000"))
        AND duration_sec <= 1800'
    ```

- Question 4: How many of the "commuter trips" are from people who are subscribers (annual or 30-day memberships)?
  * Answer: There are 582972 "commuter trips" that are taken by people who are subscribers.
  * SQL query:

    ```
    bq query --use_legacy_sql=false '
        SELECT COUNT(subscriber_type)
        FROM `bigquery-public-data.san_francisco.bikeshare_trips`
        WHERE (EXTRACT(DAYOFWEEK FROM start_date) > 1
        AND EXTRACT(DAYOFWEEK FROM start_date) <= 6)
        AND ((EXTRACT(TIME FROM start_date) >= "06:00:00.000"
        AND EXTRACT(TIME FROM start_date) <= "10:00:00.000")
        OR (EXTRACT(TIME FROM start_date) >= "16:00:00.000"
        AND EXTRACT(TIME FROM start_date) <= "20:00:00.000"))
        AND subscriber_type = "Subscriber"'
    ```

- Question 5: How many of the "commuter trips" are the start station name and the end station names differet (one way trips)?
  * Answer: There are 610493 "communter trips" that are one way trips (start station name does not equal end station name).
  * SQL query:

    ```
    bq query --use_legacy_sql=false '
        SELECT COUNT(subscriber_type)
        FROM `bigquery-public-data.san_francisco.bikeshare_trips`
        WHERE (EXTRACT(DAYOFWEEK FROM start_date) > 1
        AND EXTRACT(DAYOFWEEK FROM start_date) <= 6)
        AND ((EXTRACT(TIME FROM start_date) >= "06:00:00.000"
        AND EXTRACT(TIME FROM start_date) <= "10:00:00.000")
        OR (EXTRACT(TIME FROM start_date) >= "16:00:00.000"
        AND EXTRACT(TIME FROM start_date) <= "20:00:00.000"))
        AND start_station_name != end_station_name'
    ```
- Question 6: What hours are most bikes being checked out?
  * Answer: My SQL query returns a table that lists the count of trip_ids associated with every hour of the day. Instead of making a table showing all 24 hours, I will answer the question by saying that 8am with 132464 trips and 5pm with 126302 trips are by far the most two popular hours. Hopefully in Jupyter Notebook, I will be able to do a time trend (by hour) for the count of trips_ids.
  * SQL query:

    ```
    bq query --use_legacy_sql= false '
        SELECT MIN(EXTRACT(HOUR FROM start_date)) as hour_num, COUNT (trip_ID) as count
        FROM `bigquery-public-data.san_francisco.bikeshare_trips`
        GROUP BY EXTRACT(HOUR FROM start_date)
        ORDER BY hour_num'
    ```
- Question 7: What hours are the most bikes being checked out on weekdays?
  * Answer: Similar to question 6, 8am with 128999 trips and 5pm with 118332 trips are the two most popular hours
  * SQL query:

    ```
    bq query --use_legacy_sql= false '
        SELECT MIN(EXTRACT(HOUR FROM start_date)) as hour_num, COUNT (trip_ID) as count
        FROM `bigquery-public-data.san_francisco.bikeshare_trips`
        WHERE EXTRACT(DAYOFWEEK FROM start_date) > 1
        AND EXTRACT(DAYOFWEEK FROM start_date) <= 6
        GROUP BY EXTRACT(HOUR FROM start_date)
        ORDER BY hour_num'
    ```

- Question 8: What hours are the most bikes being checked out on weekends?
  * Answer: Instead of two peaks at 8am and 5pm shown on the weekdays, this data looks closer to a normal distribution. The rides peak around 12pm with 5726 trips and 1pm with 5767 trips. This suggests that people really are mostly using the bikes on weekdays during commute hours and on the weekends, they use them for leisure around noon.
  * SQL query:

    ```
    bq query --use_legacy_sql= false '
        SELECT MIN(EXTRACT(HOUR FROM start_date)) as hour_num, COUNT (trip_ID) as count
        FROM `bigquery-public-data.san_francisco.bikeshare_trips`
        WHERE EXTRACT(DAYOFWEEK FROM start_date) = 0
        OR EXTRACT(DAYOFWEEK FROM start_date) = 7
        GROUP BY EXTRACT(HOUR FROM start_date)
        ORDER BY hour_num'
    ```

- Question 9: During commute hours, what bucket of trip lengths (15 min, 30 min, 45 min, 60 min, over 60 min) has the most number of trips?
  * Answer: Like before, my SQL query returns a table of time range and their associated counts. Instead of writing out the table, I will answer by saying that most trips, by far, are between 0 and 15 minutes with a count of 552759. Second place is from 15 to 30 minutes with a count of 55144 trips.
  * SQL query:

    ```
    bq query --use_legacy_sql= false '
        SELECT t.time_range, COUNT(*) as count
        FROM(
            SELECT CASE
                WHEN duration_sec between 0 AND 900 THEN '15 mins'
                WHEN duration_sec between 900 AND 1800 THEN '30 mins'
                WHEN duration_sec between 1800 AND 2700 THEN '45 mins'
                WHEN duration_sec between 2700 AND 3600 THEN '60 mins'
                ELSE '60 mins plus' end as time_range
                FROM `bigquery-public-data.san_francisco.bikeshare_trips`
                WHERE (EXTRACT(DAYOFWEEK FROM start_date) > 1
                AND EXTRACT(DAYOFWEEK FROM start_date) <= 6)
                AND ((EXTRACT(TIME FROM start_date) >= "06:00:00.000"
                AND EXTRACT(TIME FROM start_date) <= "10:00:00.000")
                OR (EXTRACT(TIME FROM start_date) >= "16:00:00.000"
                AND EXTRACT(TIME FROM start_date) <= "20:00:00.000"))) t
        GROUP BY t.time_range
        ORDER BY time_range'
    ```



