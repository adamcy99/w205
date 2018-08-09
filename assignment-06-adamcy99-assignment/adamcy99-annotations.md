# My annotations, Assignment 6

**docker run -it --rm -v /home/science/w205:/w205 midsw205/base:latest bash**

The first thing I did was create a docker container. -it makes it an interactive terminal, --rm makes it so that the container is removed when exited, -v mounts the local drives to the container.

**cd assignment-06-adamcy99**

Then I changed directory into my assignment-06-adamcy99 directory

**vi docker-compose.yml**

Then I created a docker-compose.yml file with the following contents:

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
    #ports:
      #- "32181:32181"
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

  mids:
    image: midsw205/base:latest
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    extra_hosts:
      - "moby:127.0.0.1"
```

In this file, we create zookeeper, kafka, and mids containers. The zookeeper and kafka containers are off the shelf and all customization are done in the mids container. That means the only container we would maintain is the mids container. Under zookeeper, we have "expose" parameters where we listed the ports that allow kafka to connect to zookeeper. Under kafka, we have "expose" parameters where we listed the ports that allow the mids container to connect to kafka.

**curl -L -o assessment-attempts-20180128-121051-nested.json https://goo.gl/f5bRm4**

Here I downloaded the file of json data as instruction.

**exit**

Now I will exit my container and into my droplet.

**cd assignment-06-adamcy99**

Again I will enter the correct directory.

**ls**

I checked if my docker-compose.yml file and the json data file are in the folder.

**docker-compose up -d**

Here I started up the clusters.

**docker-compose logs -f kafka**

Here I am checking the kafka logs. The -f allows it to hold on to the command line and output new data as it arrives in the log file. I then exit this log with control-C.

**docker-compose ps**

Here I am checking on the running cluster.

**docker-compose logs zookeeper | grep -i binding**

This is to check the zookeeper logs for binding entries

**docker-compose exec kafka kafka-topics --create --topic foo --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181**

Here I am creating a kafka topic called foo. docker-compose exec kafka means run the command in a container. The other lines are pretty straight forward, we are creating a kafka-topic called foo with 1 partition, etc.

**docker-compose exec kafka kafka-topics --describe --topic foo --zookeeper zookeeper:32181**

Here I am just checking the topic.

**docker-compose exec mids bash -c "cat /w205/assignment-06-adamcy99/assessment-attempts-20180128-121051-nested.json"**

Here I am using jq on the linux command line to look at the json files. Notice that my json file is actually in my assignment-06 directory instead of the w205 directory. This is a change I decided to make against the original directions because I think it would be more clean to keep all assignment 6 files together.

**docker-compose exec mids bash -c "cat /w205/assignment-06-adamcy99/assessment-attempts-20180128-121051-nested.json | jq '.'"**

This is to add color and formatting so that it's more human readable.

**docker-compose exec mids bash -c "cat /w205/assignment-06-adamcy99/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c"**

This gets rid of all the white space

**docker-compose exec mids bash -c "cat /w205/assignment-06-adamcy99/assessment-attempts-20180128-121051-nested.json | jq '.[]' -c | kafkacat -P -b kafka:29092 -t foo && echo 'Produced 100 messages.'"**

Here I am using kafkacat to publish some messages to the foo topic we created in kafka.

**docker-compose exec kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic foo --from-beginning --max-messages 42**

Here we are consuming the messages from the foo topic in kafka using the kafka console consumer utility in the kafka container.

**docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t foo -o beginning -e"**

Here we are consuming the messages with the kafkacat utility in the mids container.

**docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t foo -o beginning -e" | wc -l**

Now we are using wc -l to get the number of lines to see how many messages we are seeing. This took a very long time to run.

**docker-compose down**

Tearing down the cluster

**docker-compose ps**

Check to make sure all our containers are down.


