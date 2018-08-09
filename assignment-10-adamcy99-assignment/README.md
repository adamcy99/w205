# Assignment 10

### Introduction

In this assignment, we will set up a web server that runs a simple web API service that simulates a mobile game where the user can perform actions such as *purchase a sword* or *join a guild*. Our web API service will allow us to use the curl utility to make API calls as well as write these calls to a kafka topic which we can view with the kafkacat utility. The messages sent to kafka will be in dictionary (key-value) format so that we can easily convert it to json later. The dictionary format would look like {"event_type": "purchase_sword"}. Afterwards, we will make some extensions to our printed messages to include other header information such as the host IP among other things. We will then consume the kafka topic with pyspark and be able to manipulate the messages that we’ve created using pyspark.

### Commands and Annotations 

**cd w205/assignment-10-adamcy99/**

I first navigated to the assignment directory where I will be working in.

**sudo cp ~/w205/course-content/10-Transforming-Streaming-Data/docker-compose.yml .
**

Then I copied the docker-compose.yml file from the course-content directory with the following code:

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
    expose:
      - "8888"
    ports:
      - "8888:8888"
    extra_hosts:
      - "moby:127.0.0.1"
    command: bash

  mids:
    image: midsw205/base:0.1.8
    stdin_open: true
    tty: true
    volumes:
      - ~/w205:/w205
    expose:
      - "5000"
    ports:
      - "5000:5000"
    extra_hosts:
      - "moby:127.0.0.1"
```

In this file, we create a docker cluster with 4 containers: zookeeper, kafka, mids, and spark. In the cluster, there is a virtual network that connects the containers together and allow them to communicate. For example, zookeeper and kafka are communicating through the TCP/IP port 32181 so that zookeeper can be used to manage kafka. The TCP port 5000 is the port we will use to make the API calls later on. The zookeeper, kafka, and spark containers are off the shelf and all customization are done in the mids container. That means the only container we would maintain is the mids container. Under each container, we have "expose" parameters where we listed the ports that allow kafka, zookeeper, and mids to communicate with the droplet virtual machine. Each of these containers are independent and stand-alone but can communicate with each other as well as share files using certain mounts that we can assign.

**docker run -it --rm -v /home/science/w205:/w205 midsw205/base:latest bash**

Next I created a docker container to create a new .py file. If I vi a .py file directly in the droplet, the file would be read-only. Entering the midsw205 image to create a .py file will grant me write access. -it makes it an interactive terminal, --rm makes it so that the container is removed when exited, -v mounts the local drives to the container.

**cd assignment-10-adamcy99/**

I need to navigate to the directory where I want to create the .py file.

**vi game_api_with_json_events.py**

Now we will create .py file where we will write a simple API server. The file has the following code:

```python
#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


def log_to_kafka(topic, event):
    producer.send(topic, json.dumps(event).encode())


@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "\nThis is the default response!\n"

@app.route("/purchase_a_sword")
def purchase_a_sword():
    purchase_sword_event = {'event_type': 'purchase_sword'}
    log_to_kafka('events', purchase_sword_event)
    return "\nSword Purchased!\n"

@app.route("/join_a_guild")
def join_a_guild():
    join_guild_event = {'event_type': 'join_guild'}
    log_to_kafka('events', join_guild_event)
    return "\nYou Have Joined A Guild!\n"

@app.route("/purchase_a_shield")
def purchase_a_shield():
    purchase_shield_event = {'event_type': 'purchase_shield'}
    log_to_kafka('events', purchase_shield_event)
    return "\nShield Purchased!\n"
```    
In the first few lines of the code, we are importing the json library, the KafkaProducer class from the python kafka module, and the Flask class from the flask module. Then we created a Flask object called app which is how we build our web application. We also created a KafkaProducer object called producer which we initialize by telling it to connect to kafka through the 29092 port. Then we created a function called log_to_kafka which will send the events we create into our kafka topic through the producer object. Then we used the route decorator with our app object to add a url rule for our default_response(), purchase_a_sword(), join_a_guild(), and purchase_a_shield() functions. In each of the functions, we create an a dictionary object. For example, in the purchase_a_sword() function, we created the purchase_a_sword_event dictionary object that has "event_type" as a key, and "purchase_sword" as the value. Then we run our log_to_kafka() function, where we will pass our purchase_a_sword_event (dictionary object) into a kafka topic that we will name "events". Then we will return a "Sword Purchased" output to the command line each time we make a web API call to purchase a sword.

**exit**

Now we will exit our midsw205 container.

**ls -l**

Now we will see that our new game_api.py file is in our directory.

**docker-compose up -d**

Now I am starting up the cluster.

**docker-compose exec kafka kafka-topics --create --topic events --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181**

Here I am creating a kafka topic called "events". docker-compose exec kafka means run the command in a container. The other lines are pretty straight forward, we are creating a kafka-topic called "tests" with 1 partition, we are pairing kafka with zookeeper through the 32181 port so that zookeeper can manage kafka, etc. We get the output: ‘Created topic "events".’ When our kafka topic is created.

**docker-compose exec mids env FLASK_APP=/w205/assignment-10-adamcy99/game_api_with_json_events.py flask run --host 0.0.0.0**

This command runs the python flask script in the mids container of our docker cluster.  We will be able to see the outputs of our python program on the command line here as we make the web API calls.

**Open a new window and navigate to w205/assignment-10-adamcy99/**

Now, we can open a new window and navigate to the same directory. We will use the curl utility to make web API calls.

**docker-compose exec mids curl http://localhost:5000/**

Here we are making an API call with curl. As mentioned before, we are using the TCP port 5000 to make the API call. In this case we are not specifying a function such as purchase sword, or join guild. Therefore, when we run this command, we get the output "This is the default response!". In our other window where we are running the python flask API server, we get the output "127.0.0.1 - - [16/Jul/2018 03:21:05] "GET / HTTP/1.1" 200 -". Here, we see the IP address of our host server, a time stamp, and our GET command. We also see HTTP/1.1 which is stays connected after the call while HTTP/1.0 hangs up.

**docker-compose exec mids curl http://localhost:5000/purchase_a_sword**

Now we are making another API call with curl, but this time we are using the purchase_a_sword function. We get the "Sword Purchased!" response, while in the other window where we are running the python flask API server, we get the output "127.0.0.1 - - [16/Jul/2018 03:27:25] "GET /purchase_a_sword HTTP/1.1" 200 -" IT is similar to before except we can see now that we are purchasing a sword.

**docker-compose exec mids curl http://localhost:5000/join_a_guild**

Similar to the previous two commands, except now we are making an API call with curl and using the join_a_guild function. We get the output "You Have Joined A Guild!" and in our other window where we are running the python flask API server, we get the output "127.0.0.1 - - [16/Jul/2018 03:29:24] "GET /join_a_guild HTTP/1.1" 200 -". 

**docker-compose exec mids curl http://localhost:5000/purchase_a_shield**

Similar to the previous commands, except now we are making an API call with curl and using the purchase_a_shield function. We get the output "Shield Purchased!" and in our other window where we are running the python flask API server, we get the output "127.0.0.1 - - [16/Jul/2018 03:29:24] "GET /purchase_a_shield HTTP/1.1" 200 -". 

**docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning -e**

Now we will use the kafkacat utility to consume the messages that our web service wrote to the kafka "events" topic. Our kafka topic has the following messages:

{"event_type": "default"}

{"event_type": "purchase_sword"}

{"event_type": "join_guild"}

{"event_type": "purchase_shield"}

As you can see, these are the dictionary objects that we created in our game_api_with_json_events.py code.

Now we are going to create a new python file called game_api_with_extended_json_events.py which is similar to the one we created before, except with more key-value attributes.

**docker run -it --rm -v /home/science/w205:/w205 midsw205/base:latest bash**

**cd assignment-10-adamcy99/**

Again we have to created a docker container to create the new .py file because of read-only restrictions in the droplet. Then I navigated to the desired directory.

**vi game_api_with_extended_json_events.py**

Now we will create the new file with our desired changes. The file has the following code:

```python
#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())


@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "\nThis is the default response!\n"


@app.route("/purchase_a_sword")
def purchase_a_sword():
    purchase_sword_event = {'event_type': 'purchase_sword'}
    log_to_kafka('events', purchase_sword_event)
    return "\nSword Purchased!\n"

@app.route("/join_a_guild")
def join_a_guild():
    join_guild_event = {'event_type': 'join_guild'}
    log_to_kafka('events', join_guild_event)
    return "\nYou Have Joined A Guild!\n"

@app.route("/purchase_a_shield")
def purchase_a_shield():
    purchase_shield_event = {'event_type': 'purchase_shield'}
    log_to_kafka('events', purchase_shield_event)
    return "\nShield Purchased!\n"
```

The big change in this code is the line: event.update(request.headers). This line of code is taking the dictionary events we wrote in the form of {‘event_type’: default_event} and adding headers to it that includes the host IP among other things before publishing it to kafka.

**docker-compose exec mids env FLASK_APP=/w205/assignment-10-adamcy99/game_api_with_extended_json_events.py flask run --host 0.0.0.0**

Now we will run the python flask script again in the mids container of our docker cluster to see the outputs of our python program as we make the web API calls.

**docker-compose exec mids curl http://localhost:5000/**

**docker-compose exec mids curl http://localhost:5000/purchase_a_sword**

**docker-compose exec mids curl http://localhost:5000/join_a_guild**

**docker-compose exec mids curl http://localhost:5000/purchase_a_shield**

In the other window, we will run these curl utility commands again to make the API calls.

**docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning -e**

Again, we will use the kafkacat utility to consume the messages that our web service wrote to the kafka "events" topic. Our kafka topic has the following messages:

{"event_type": "default"}

{"event_type": "purchase_sword"}

{"event_type": "join_guild"}

{"event_type": "purchase_shield"}

{"Host": "localhost:5000", "event_type": "default", "Accept": "*/*", "User-Agent": "curl/7.47.0"}

{"Host": "localhost:5000", "event_type": "purchase_sword", "Accept": "*/*", "User-Agent": "curl/7.47.0"}

{"Host": "localhost:5000", "event_type": "join_guild", "Accept": "*/*", "User-Agent": "curl/7.47.0"}

{"Host": "localhost:5000", "event_type": "purchase_shield", "Accept": "*/*", "User-Agent": "curl/7.47.0"}

You will notice that our first 4 messages from the old format is still in our kafka topic. In addition we have 4 new messages with the new format which includes "Host" key-value pairs, "Accept" key-value pairs, and "User_Agent" key-value pairs. 

**docker-compose exec spark pyspark**

Now we will run a pyspark shell.

**raw_events = spark.read.format("kafka").option("kafka.bootstrap.servers", "kafka:29092").option("subscribe","events").option("startingOffsets", "earliest").option("endingOffsets", "latest").load()**

Then we will use pyspark to consume the kafka "events" topic and store it under raw_events.

**raw_events.cache()**

Now we will cache our raw events.


**raw_events.printSchema()**

**raw_events.show()**

When we look at the schema of our raw_events as well as what’s in the data frame itself, we notice that our values are in binary form and not quite readable. 

**events = raw_events.select(raw_events.value.cast('string’))**

Therefore, we will will create a new data frame called events that will store the values as a string.

**events.printSchema()**

**events.show()**

Now we see that are event values are shown as strings instead of binary.

**import json**

**extracted_events = events.rdd.map(lambda x: json.loads(x.value)).toDF()**

Now we will create a new data frame called extracted_events where we will extract our values from the events data frame into individual json objects.

**extracted_events.show()**

Now when we show our extracted_events data frame, we will see:

| event_type         |
| :-------------:    |
| default            |
| purchase_sword     |
| join_guild         |
| purchase_shield    |
| default            |
| purchase_sword     |
| join_guild         |
| purchase_shield    |

which are nicely formated objects. 

**exit()**

We will now exit pyspark.

**Exit flask with control-C**

We will exit flask with control-C.

**docker-compose down**

Finally, tear down our cluster.

### Appendix:

1. I created functions to join_a_guild and purchase_a_shield in the game_api.py file.

2. I ran all of the functions including the default function, purchase_a_sword, join_a_guild, and purchase_a_shield so we can see them all when we use kafkacat.

3. I used the show() and printSchema methods on the raw_events and events data frames to illustrate that the objects are stored in binary, and then in string format.



