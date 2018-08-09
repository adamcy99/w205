# My Annotations, Assignment 8

### Introduction

In this assignment, our main goal is to create a kafka topic, publish json messages from a downloaded file to that topic, and then use pyspark to subscribe to the topic. using spark's parallel method's we can manipulate large data frames and then using core python and pandas, we can manipulate individual json objects to take a closer look. We will also convert the data in json format and then convert that into a spark temporary table. We will then use spark sql to query from the temporary table and save the resulting data frame from our query into a parquet file saved in the hadoop hdfs.

**ls**

After I get into my droplet, the first thing I do is use the ls command to list all of the files and directories in my current directory. This gives me a sense of which directory I am in, and also helps me figure out my path to the directory I want to end up in.

**cd w205/assignment-08-adamcy99/**

I then use the cd command to navigate to into the directory for this assignment.

**cp ~/w205/course-content/08-Querying-Data/docker-compose.yml .**

Instead of creating a new docker-compose.yml file as I did in the past, this time I copied the file provided for us in the course-content directory. I was running into some permission errors, so I had to use the sudo command to complete this copy.

The docker-compose.yml file has the following contents:

```yml
---
version: '2'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 32181
      ZOOKEEPER_TICK_TIME: 2000
    expose:
      - "2181"
      - "2888"
      - "32181"
      - "3888"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:32181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    expose:
      - "9092"
      - "29092"

  cloudera:
    image: midsw205/cdh-minimal:latest
    expose:
      - "8020" # nn
      - "50070" # nn http
      - "8888" # hue
    #ports:
    #- "8888:8888"

  spark:
    image: midsw205/spark-python:0.0.5
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    command: bash
    depends_on:
      - cloudera
    environment:
      HADOOP_NAMENODE: cloudera

  mids:
    image: midsw205/base:latest
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205

```

In this file, we create a docker cluster with five containers: zookeeper, kafka, cloudera, spark, and mids. In the cluster, there is a virtual network that connects the containers together and allow them to communicate. For example, zookeeper and kafka are communicating through the TCP/IP port 32181 so that zookeeper can be used to manage kafka. The zookeeper, kafka, cloudera and spark containers are off the shelf and all customization are done in the mids container. That means the only container we would maintain is the mids container. Under zookeeper and kafka, we have "expose" parameters where we listed the ports that allow kafka and zookeeper to communicate with the droplet virtual machine. Each of these containers are independent and stand-alone but can communicate with each other as well as share files using certain mounts that we can assign.

**docker run -it --rm -v /home/science/w205:/w205 midsw205/base:latest bash**

Next I created a docker container to download the json data file. I couldn't do it directly in the droplet because of permission issues. -it makes it an interactive terminal, --rm makes it so that the container is removed when exited, -v mounts the local drives to the container.

**cd assignment-07-adamcy99**

I changed directory into my assignment-07-adamcy99 directory because that's where I want the file to be saved.

**curl -L -o assessment-attempts-20180128-121051-nested.json https://goo.gl/f5bRm4**

Here we are using the curl utility to download the json data file from the internet.

**exit**

Now I will exit my container back into the droplet.

**cd w205/assignment-07-adamcy99/**

In the droplet, I navigate back to the directory for this assignment.

**ls**

I wanted to make sure my docker-compose.yml file and json data file are in the cluster.

**docker-compose up -d**

Here I started up the cluster. 

**docker-compose ps**

Here I am checking to see if all the containers are up and running.

**docker-compose logs -f kafka**

Here I am checking the kafka logs. The -f allows it to hold on to the command line and output new data as it arrives in the log file. I then exit this log with control-C.

**docker-compose exec cloudera hadoop fs -ls /tmp/**

I used the above command to look at what's inside of the hdfs /tmp directory. The hadoop hdfs is separate from the local linux file system and thus has a different path as well. Therefore, we have to use the above command to do an "ls command" for the hadoop file system.

**docker-compose exec kafka kafka-topics --create --topic tests --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181**

Here I am creating a kafka topic called "tests". docker-compose exec kafka means run the command in a container. The other lines are pretty straight forward, we are creating a kafka-topic called "tests" with 1 partition, etc.

**docker-compose exec kafka kafka-topics --describe --topic tests --zookeeper zookeeper:32181**

Here I am describing the kafka topic to check it. I see that the topic name is tests, the PartitionCount is 1, the ReplicationFactor is 1, etc.

**docker-compose exec mids bash -c "cat /w205/assignment-08-adamcy99/assessment-attempts-20180128-121051-nested.json"**

Now we are executing a bash shell command as microservices, where we start a container, run a command, and then exit the container when the command is completed. Here we are just printing the json file as it is.

**docker-compose exec mids bash -c "cat /w205/assignment-08-adamcy99/assessment-attempts-20180128-121051-nested.json | jq '.'"**

Next, we do the same thing as above, except now we pipe it through the jq utility for formatting and coloring so it's more human readable.

**docker-compose exec mids bash -c "cat /w205/assignment-08-adamcy99/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c"**

In regular json files, there is a wrapper around the json objects that consists of an open square bracket at the beginning of the file, comma separated json objects, and then a close square bracket at the end of the file. Here we are using jq to remove the outer wrapper and also compacts the formatting to get rid of the blank spaces so it's easier for computers to read.

**docker-compose exec mids bash -c "cat /w205/assignment-08-adamcy99/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | kafkacat -P -b kafka:29092 -t tests"**

Now we are executing a bash shell again in the mids container to run a microservice to pipe the json file into the jq utility. Then, we pipe it into the kafkacat utility with the -P option which tells it to publish messages. The -t option gives the topic name of "tests" and the kafka:29092 tells it the container name and the port number where kafka is running. This command publishes the json objects from the file into the kafka topic.

**docker-compose exec spark pyspark**

Here we are starting pyspark which allows us to use spark through python.

**raw_messages = spark.read.format("kafka").option("kafka.bootstrap.servers", "kafka:29092").option("subscribe","commits").option("startingOffsets", "earliest").option("endingOffsets", "latest").load()**

Here we are consuming the kafka messages and storing them into a data frame called "raw_messages".

**raw_messages.cache()**

Spark uses "lazy evaluation" which will give a warning message every time something isn't in memory. The code above will cache the spark data structure so that the warning messages don't appear.

**raw_messages.printSchema()**

Here we are running a method to print the schema of our data frame. Here are some of the outputs of our schema: key: binary (nullable = true), value: binary (nullable = true), etc. Notice that our data is stored as binary at this time.

**raw_messages.show()**

This method shows us our messages. However, our messages are stored in binary form so it is very hard to read at this time. We have our headers of key, value, topic, partition, offset, timestamp, and timestampType. 

**messages = raw_messages.select(raw_messages.value.cast('string'))**

To help us read the messages, we are now creating a new data frame called messages that stores the messages after we translate the value into strings. 

**messages.show()**

Now we can take a look at the values of our messages in a readable format. We see that under value column, we can see {"keen_timestamp"..., they look like the beginning of each of our json objects.

**messages.printSchema()**

Now we can take a look at the schema again and we will see value: string (nullable = true). We can see that now our messages are stored in the string format.

**messages.write.parquet("/tmp/messages")**

This writes the messages data frame into a parquet file in the hadoop hdfs. Again, the hadoop hdfs is a separate file system from our local linux file system. The hadoop hdfs has a virtual presence on all the nodes in the hadoop cluster. Parquet is a binary columnar format that we are saving the data frame as. This format is immutable which allows it to be pushed out of the hadoop cluster, stored in object store, delivered in content delivery networks, etc.

**import json**

We need to import the json library for the next step.

**extracted_messages = messages.rdd.map(lambda x: json.loads(x.value)).toDF()**

Here we are extracting our messages as json format into a new data frame.

**extracted_messages.show()**

Now we can take a look at our new data frame. The data is now in nested json form instead of a single line of strings per message.

**extracted_messages.printSchema()**

Now when we print the schema, we can see base_exam_id, cetification, exam_name, etc. as columns, we can even see the sequences column and its many layers.

**extracted_messages.registerTempTable('messages')**

We can now used this data frame and the registerTempTable() method to create a spark temporary table called "messages". This will allow us to use spark sql to deal with the nested json.

**spark.sql("select exam_name from messages limit 10").show()**

Here I am using spark sql commands to query the temporary table and making it show me the first 10 exam names.

**spark.sql("select base_exam_id, certification, exam_name, max_attempts, started_at, user_exam_id, sequences.questions[0].user_incomplete from messages limit 10").show()**

Here I am pulling out the base_exam_id, certification, exam_name, max_attempts, started_at, user_exam_id, and whether or not the first question is incomplete or not.

**some_exam_info = spark.sql("select base_exam_id, certification, exam_name, max_attempts, started_at, user_exam_id, sequences.questions[0].user_incomplete from messages limit 10")**

Here I am saving the data that I pulled out into a new data frame.

**some_exam_info = some_exam_info.withColumnRenamed("sequences[questions] AS `questions`[0][user_incomplete]", "Finish_First_Question?")**

Here I renamed the column name of the last column from "sequences[questions] AS `questions`[0][user_incomplete]" to "Finish_First_Qeustion?" because it was long and ugly.

**some_exam_info.write.parquet("/tmp/some_exam_info")**

As we did before with the "messages" data frame, we are now saving our query data frame into hadoop hdfs.

**exit()**

Now we can exit pyspark.

**docker-compose exec cloudera hadoop fs -ls /tmp/**

Now we can use the ls command to see what directories are in our tmp directory in the hadoop hdfs. we can see that our /tmp/some_exam_info directory is in the hadoop hdfs.

**docker-compose exec cloudera hadoop fs -ls /tmp/some_exam_info/**

Now we can go into that /tmp/some_exam_info directory and see what's inside. We have /tmp/some_exam_info/_SUCCESS and /tmp/some_exam_info/part-00000-86024fb7-a5f5-4cda-9154-73024c36bc62-c000.snappy.parquet.

**docker-compose down**

Tear down the docker cluster.

**docker-compose ps**

Make sure everything is torn down.

### Appendix

  1. I saved the json data file into my assignment 8 folder so the paths for the jq commands, etc. are all changed.

  2. I decided to name to kafka topic "tests" instead of "foo".

  3. Before using kafkacat to publish the json dataset to the kafka topic, I explored the json file with jq.

  4. Decided to call the data consumed from the kafka topic, "raw_messages" instead of "raw_commits".

  5. Decided to show the raw_messages and messages data frames so the reader can get an idea of what is going on.

  6. Our data file is different so I had to choose how to look at our new json objects. I chose to look at the 'exam_name' of the object because that is most interesting to me.

  7. I decided to use spark sql to pull base_exam_id, certification, exam_name, max_attempts, started_at, user_exam_id, and whether or not the first question is incomplete or not to put into a new data frame and them use parquet to save into hadoop hdfs.

  8. I used the withColumnRenamed() method to change the column name of the last column to something less ugly.





