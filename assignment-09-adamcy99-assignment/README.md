# Assignment 9

### Introduction

In this assignment, we will set up a web server that runs a simple web API service that simulates a mobile game where the user can perform actions such as *purchase a sword* or *join a guild*. We will use curl to make web API calls to our web service and examine the behaviors and outputs. We will then modify our web API service so that besides allowing API calls, it will also write these calls to a kafka topic which we can view with kafkacat.

### Commands and Annotations 

**cd w205/assignment-09-adamcy99/**

I first navigated to the assignment directory where I will be working in.

**vi docker-compose.yml**

Then created a docker-compose.yml file with the following code:

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

  mids:
    image: midsw205/base:0.1.8
    stdin_open: true
    tty: true
    volumes:
      - /home/science/w205:/w205
    expose:
      - "5000"
    ports:
      - "5000:5000"
    extra_hosts:
      - "moby:127.0.0.1"
```
In this file, we create a docker cluster with 3 containers: zookeeper, kafka, and mids. In the cluster, there is a virtual network that connects the containers together and allow them to communicate. For example, zookeeper and kafka are communicating through the TCP/IP port 32181 so that zookeeper can be used to manage kafka. The TCP port 5000 is the port we will use to make the API calls later on. The zookeeper and kafka containers are off the shelf and all customization are done in the mids container. That means the only container we would maintain is the mids container. Under each container, we have "expose" parameters where we listed the ports that allow kafka, zookeeper, and mids to communicate with the droplet virtual machine. Each of these containers are independent and stand-alone but can communicate with each other as well as share files using certain mounts that we can assign.

**docker-compose up -d**

Now I am starting up the cluster.

**docker-compose exec kafka kafka-topics --create --topic events --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181**

Here I am creating a kafka topic called “events”. docker-compose exec kafka means run the command in a container. The other lines are pretty straight forward, we are creating a kafka-topic called "tests" with 1 partition, we are pairing kafka with zookeeper through the 32181 port so that zookeeper can manage kafka, etc. We get the output: ‘Created topic “events”.’ When our kafka topic is created.

**docker run -it --rm -v /home/science/w205:/w205 midsw205/base:latest bash**

Next I created a docker container to create a new .py file. If I vi a .py file directly in the droplet, the file would be read-only. Entering the midsw205 image to create a .py file will grant me write access. -it makes it an interactive terminal, --rm makes it so that the container is removed when exited, -v mounts the local drives to the container.

**cd assignment-09-adamcy99/**

I need to navigate to the directory where I want to create the .py file.

**vi game_api.py**

Now we will create .py file where we will write a simple API server. The file has the following code:

```python
#!/usr/bin/env python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def default_response():
    return "\nThis is the default response!\n"

@app.route("/purchase_a_sword")
def purchase_sword():
    # business logic to purchase sword
    return "\nSword Purchased!\n"

@app.route("/join_a_guild")
def join_guild():
    # business logic to join guild
    return "\nYou Have Joined A Guild!\n"

@app.route("/purchase_a_shield")
def purchase_shield():
    # business logic to purchase a shield
    return "\nShield Purchased!\n”
```

Here we are using the python flask module to write the API server. We are importing the flask library in the first few lines. Then we wrote three functions to purchase a sword, join a guild, and purchase a shield. With this, every time the user performs the actions of purchasing a sword, shield or joining a guild, we will make API calls to the API server.

**exit**

Now we will exit our midsw205 container.

**ls -l**

Now we will see that our new game_api.py file is in our directory.

**docker-compose exec mids env FLASK_APP=/w205/assignment-09-adamcy99/game_api.py flask run**

This command runs the python script and we will be able to see the outputs of our python program here as we make the web API calls.

**Open a new window and navigate to w205/assignment-09-adamcy99/**

Now, we can open a new window and navigate to the same directory. We will use curl to make web API calls.

**docker-compose exec mids curl http://localhost:5000/**

Here we are making an API call with curl. As mentioned before, we are using the TCP port 5000 to make the API call. In this case we are not specifying a function such as purchase sword, or join guild. Therefore, when we run this command, we get the output “This is the default response!”. In our other window where we are running the python flask API server, we get the output “127.0.0.1 - - [16/Jul/2018 03:21:05] "GET / HTTP/1.1" 200 -“. Here, we see the IP address of our host server, a time stamp, and our GET command. We also see HTTP/1.1 which is stays connected after the call while HTTP/1.0 hangs up.

**docker-compose exec mids curl http://localhost:5000/purchase_a_sword**

Now we are making another API call with curl, but this time we are using the purchase_a_sword function. We get the “Sword Purchased!” response, while in the other window where we are running the python flask API server, we get the output “127.0.0.1 - - [16/Jul/2018 03:27:25] "GET /purchase_a_sword HTTP/1.1" 200 -“ IT is similar to before except we can see now that we are purchasing a sword.

**docker-compose exec mids curl http://localhost:5000/join_a_guild**

Similar to the previous two commands, except now we are making an API call with curl and using the join_a_guild function. We get the output “You Have Joined A Guild!” and in our other window where we are running the python flask API server, we get the output “127.0.0.1 - - [16/Jul/2018 03:29:24] "GET /join_a_guild HTTP/1.1" 200 -“. 

**Stop flask with control-C**

In our flask window, we will stop flask with control-C. We will now be making changes to our game_api.py file.

**docker run -it --rm -v /home/science/w205:/w205 midsw205/base:latest bash**

Like before, to edit our game_api.py file, we have to start a midsw205 container to get write access.

**cd assignment-09-adamcy99/**

Navigate to the correct directory.

**vi game_api.py**

Now we will open up the game_api.py file to make some changes. The resulting file has the following code:

```python
#!/usr/bin/env python
from kafka import KafkaProducer
from flask import Flask
app = Flask(__name__)
event_logger = KafkaProducer(bootstrap_servers='kafka:29092')
events_topic = 'events'

@app.route("/")
def default_response():
    event_logger.send(events_topic, 'default'.encode())
    return "\nThis is the default response!\n"

@app.route("/purchase_a_sword")
def purchase_sword():
    # business logic to purchase sword
    # log event to kafka
    event_logger.send(events_topic, 'purchased_sword'.encode())
    return "\nSword Purchased!\n"

@app.route("/join_a_guild")
def join_guild():
    # business logic to join guild
    # log event to kafka
    event_logger.send(events_topic, 'joined_guild'.encode())
    return "\nYou Have Joined A Guild!\n"

@app.route("/purchase_a_shield")
def purchase_shield():
    # business logic to purchase a shield
    # log event to kafka
    event_logger.send(events_topic, 'purchased_shield'.encode())
    return "\nShield Purchased!\n”
```
Now, in each of the functions, we added an event_logger.send() line. With this, we will have the extra functionality of publishing to the kafka “events” topic.

**exit**

Now we will exit our midsw205 container.

**docker-compose exec mids env FLASK_APP=/w205/assignment-09-adamcy99/game_api.py flask run**

Again we use this command to run the python script so we can see the outputs of our python program here as we make the web API calls.

***docker-compose exec mids curl http://localhost:5000/**

In our other window, we will run this command again on the linux command line. Again, we get the output “This is the default response!” and in our other window, we still get “127.0.0.1 - - [16/Jul/2018 03:47:27] "GET / HTTP/1.1" 200 -“

**docker-compose exec mids curl http://localhost:5000/purchase_a_sword**

**docker-compose exec mids curl http://localhost:5000/join_a_guild**

**docker-compose exec mids curl http://localhost:5000/purchase_a_shield**

**docker-compose exec mids curl http://localhost:5000/purchase_a_shield**

**docker-compose exec mids curl http://localhost:5000/purchase_a_sword**

Now we will spam a few of these API calls. Our flask window has the following outputs:

127.0.0.1 - - [16/Jul/2018 03:47:27] "GET / HTTP/1.1" 200 -

127.0.0.1 - - [16/Jul/2018 03:51:12] "GET /purchase_a_sword HTTP/1.1" 200 -

127.0.0.1 - - [16/Jul/2018 03:51:19] "GET /join_a_guild HTTP/1.1" 200 -

127.0.0.1 - - [16/Jul/2018 03:51:26] "GET /purchase_a_shield HTTP/1.1" 200 -

127.0.0.1 - - [16/Jul/2018 03:51:31] "GET /purchase_a_shield HTTP/1.1" 200 -

127.0.0.1 - - [16/Jul/2018 03:51:36] "GET /purchase_a_sword HTTP/1.1" 200 -

**docker-compose exec mids bash -c "kafkacat -C -b kafka:29092 -t events -o beginning -e”**

Now we will use kafkacat to consume the messages that our web service wrote to the kafka “events” topic. Our kafka topic has the following messages:

default

purchased_sword

joined_guild

purchased_shield

purchased_shield

purchased_sword

**docker-compose down**

Now we can use control-C to stop flask and tear down our cluster.

### Appendix:

1. I created functions to join_a_guild and purchase_a_shield in the game_api.py file.

2. I ran many of the functions such as purchase_a_shield, purchase_a_sword, etc. in random order so we can see them all when we use kafkacat.



