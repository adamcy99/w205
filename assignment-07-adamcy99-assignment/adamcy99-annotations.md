# My annotations, Assignment 7

### Introduction

In this assignment, our main goal is to create a kafka topic, publish json messages from a downloaded file to that topic, and then use pyspark to subscribe to the topic. using spark's parallel method's we can manipulate large data frames and then using core python and pandas, we can manipulate individual json objects to take a closer look.

**ls**

After I get into my droplet, the first thing I do is use the ls command to list all of the files and directories in my current directory. This gives me a sense of which directory I am in, and also helps me figure out my path to the directory I want to end up in.

**cd w205/assignment-07-adamcy99/**

I then use the cd command to navigate to into the directory for this assignment.

**sudo cp ~/w205/course-content/07-Sourcing-Data/docker-compose.yml .**

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
    extra_hosts:
      - "moby:127.0.0.1"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:32181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - ~/w205:/w205
    expose:
      - "9092"
      - "29092"
    extra_hosts:
      - "moby:127.0.0.1"

  spark:
    image: midsw205/spark-python:0.0.5
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    command: bash
    extra_hosts:
      - "moby:127.0.0.1"

  mids:
    image: midsw205/base:latest
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    extra_hosts:
      - "moby:127.0.0.1"

```
In this file, we create a docker cluster with four containers: zookeeper, kafka, spark, and mids. In the cluster, there is a virtual network that connects the containers together and allow them to communicate. For example, zookeeper and kafka are communicating through the TCP/IP port 32181 so that zookeeper can be used to manage kafka. The zookeeper, kafka, and spark containers are off the shelf and all customization are done in the mids container. That means the only container we would maintain is the mids container. Under zookeeper and kafka, we have "expose" parameters where we listed the ports that allow kafka and zookeeper to communicate with the droplet virtual machine. Each of these containers are independent and stand-alone but can communicate with each other as well as share files using certain mounts that we can assign.

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

**docker-compose exec kafka kafka-topics --create --topic foo --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181**

Here I am creating a kafka topic called foo. docker-compose exec kafka means run the command in a container. The other lines are pretty straight forward, we are creating a kafka-topic called foo with 1 partition, etc. 

**docker-compose exec kafka kafka-topics --describe --topic foo --zookeeper zookeeper:32181**

Here I am describing the kafka topic to check it. I see that the topic name is foo, the PartitionCount is 1, the ReplicationFactor is 1, etc.

**docker-compose exec mids bash -c "cat /w205/assignment-07-adamcy99/assessment-attempts-20180128-121051-nested.json"**

Now we are executing a bash shell command as microservices, where we start a container, run a command, and then exit the container when the command is completed. Here we are just printing the json file as it is.

**docker-compose exec mids bash -c "cat /w205/assignment-07-adamcy99/assessment-attempts-20180128-121051-nested.json | jq '.'"**

Next, we do the same thing as above, except now we pipe it through the jq utility for formatting and coloring so it's more human readable.

**docker-compose exec mids bash -c "cat /w205/assignment-07-adamcy99/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c"**

In regular json files, there is a wrapper around the json objects that consists of an open square bracket at the beginning of the file, comma separated json objects, and then a close square bracket at the end of the file. Here we are using jq to remove the outer wrapper and also compacts the formatting to get rid of the blank spaces so it's easier for computers to read.

**docker-compose exec mids bash -c "cat /w205/assignment-07-adamcy99/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | kafkacat -P -b kafka:29092 -t foo && echo 'Produced 100 messages.'"**

Now we are executing a bash shell again in the mids container to run a microservice to pipe the json file into the jq utility. Then, we pipe it into the kafkacat utility with the -P option which tells it to publish messages. The -t option gives the topic name of foo and the kafka:29092 tells it the container name and the port number where kafka is running. This command publishes the json objects from the file into the kafka topic.

**docker-compose exec spark pyspark**

Here we are starting pyspark which allows us to use spark through python.

**messages = spark.read.format("kafka").option("kafka.bootstrap.servers", "kafka:29092").option("subscribe","foo").option("startingOffsets", "earliest").option("endingOffsets", "latest").load()**

Here we are consuming the messages and storing them into a data frame called "messages".

**messages.printSchema()**

Here we are running a method to print the schema of our data frame. Here are some of the outputs of our schema: key: binary (nullable = true), value: binary (nullable = true), etc. Notice that our data is stored as binary at this time.

**messages.show()**

This method shows us our messages. However, our messages are stored in binary form so it is very hard to read at this time. We have our headers of key, value, topic, partition, offset, timestamp, and timestampType. 

**messages_as_strings=messages.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")**

To help us read the messages, we are now creating a new data frame called messages_as_strings that stores the messages after we translate the key and value into strings. 

**messages_as_strings.show()**

Now we can take a look at the key and values of our messages in a readable format. We see that the keys are all still null, but under value, we can see {"keen_timestamp"..., they look like the beginning of each of our json objects.

**messages_as_strings.printSchema()**

Now we can take a look at the schema again and we will see key: string (nullable = true), value: string (nullable = true). We can see that now our messages are stored in the string format.

**messages_as_strings.count()**

This method lets us know how many items are in our data frame. We have 3280 items.

**messages_as_strings.select('value').take(1)**

Now we try to extract individual data from our data frame. We end up with a json object that is very long and very hard to read. 

**messages_as_strings.select('value').take(1)[0].value**

Now we only want to see the value of the same item. What we end up with is not much better.

**import json**

Now we will use the python core and pandas methods to manipulate 1 record so that we can take a look of what it looks like. It would not be wise to do this on every record because it will take forever. Spark's parallel methods enabled us to manipulate the entire data frame earlier in pretty short amounts of time. This would not be possible for core python so we are only going to look at 1 record.

**first_message=json.loads(messages_as_strings.select('value').take(1)[0].value)**

Here we are creating a new data frame and storing the first item in our previous data frame into it. However, we are loading it in json format so that we can manipulate it.

**first_message**

Here we are printing our new data frame which has 1 entry, we can see that the output looks similar as before, however, we can look at how we can manipulate into this json object to get specific information.

**print(first_message['exam_name'])**

Here we are taking a look at what the exam name is for the first object. The result is Normal Forms and All That Jazz Master Class.

**print(first_message['sequences']['questions'][0]['user_result'])**

This is going a bit deeper into the json object to look at whether the person was able to solve the first question of the exam. 

**fifth_message=json.loads(messages_as_strings.select('value').take(5)[4].value)**

Now lets take the value of our 5th json object to see what it looks like. We will store it as fifth_message.

**print(fifth_message['exam_name'])**

The fifth exam name is called Introduction to Big Data.

**print(fifth_message['sequences']['questions'][0]['user_result'])**

The result here is 'incorrect' which means that the person solved the first question of this exam incorrectly.

**exit()**

Exit pyspark using a well formed method.

**docker-compose down**

Tear down the docker cluster.

**docker-compose ps**

Make sure everything is torn down.

### Appendix

  1. I saved the json data file into my assignment 7 folder so the paths for the jq commands, etc. are all changed.

  2. Our data file is different so I had to choose how to look at our new json objects. I chose to look at the 'exam_name' of the object because that is most interesting to me.

  3. To avoid making the work look so easy, I also decided to dig deeper into the json object. I used print(first_message['sequences']['questions'][0]['user_result']).

  4. I also repeated the steps, except I looked at the 5th message as well. fifth_message=json.loads(messages_as_strings.select('value').take(5)[4].value)

5. Same as with the 1st message, I looked at the ‘exam name of the 5th message.

6. Same as with the 1st message, I also dogged deeper into the 5th message. print(fifth_message['sequences']['questions'][0]['user_result'])



