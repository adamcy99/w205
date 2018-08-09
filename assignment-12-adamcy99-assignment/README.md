# Assignment 12

### Introduction

In this assignment, we will set up a web server that runs a simple web API service that simulates a mobile game where the user can perform actions such as *purchase a sword* or *join a guild*. Our web API service will allow us to use the Apache Bench utility to make many API calls as well as write these calls to a kafka topic which we can view with the kafkacat utility. The messages sent to kafka will be in dictionary (key-value) format so that we can easily convert it to json later. The dictionary format would look like {"event_type": "purchase_sword"}. We also included some extensions to our printed messages to include other header information such as the host IP among other things. We have 2 other python codes: just_filtering.py which will allow us to filter the events that we want with multiple schemas, and filtered_writes.py which will write our events to hadoop hdfs in the parquet format. Then we will use Jupyter Notebook to Query our events from hadoop hdfs.

### Commands and Annotations 

**cd w205/assignment-12-adamcy99/**

I first navigated to the assignment directory where I will be working in.

**sudo cp ~/w205/course-content/12-Querying-Data-II/docker-compose.yml .**

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

  cloudera:
    image: midsw205/cdh-minimal:latest
    expose:
      - "8020" # nn
      - "50070" # nn http
      - "8888" # hue
    #ports:
    #- "8888:8888"
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
    depends_on:
      - cloudera
    environment:
      HADOOP_NAMENODE: cloudera
    extra_hosts:
      - "moby:127.0.0.1"
    command: bash

  mids:
    image: midsw205/base:0.1.9
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

In this file, we create a docker cluster with 5 containers: zookeeper, kafka, mids, cloudera, and spark. In the cluster, there is a virtual network that connects the containers together and allow them to communicate. For example, zookeeper and kafka are communicating through the TCP/IP port 32181 so that zookeeper can be used to manage kafka. The TCP port 5000 is the port we will use to make the API calls later on. The zookeeper, kafka, cloudera, and spark containers are off the shelf and all customization are done in the mids container. That means the only container we would maintain is the mids container. Under each container, we have "expose" parameters where we listed the ports that allow each container to communicate with the droplet virtual machine. Each of these containers are independent and stand-alone but can communicate with each other as well as share files using certain mounts that we can assign.

**sudo cp ~/w205/course-content/12-Querying-Data-II/*.py .**

Now we used the above command to copy all the .py files from the course-content/12-Querying-Data-II directory. These 3 files are: game_api.py, filtered_writes.py, and just_filtering.py.

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
    return "This is the default response!\n"

@app.route("/purchase_a_sword")
def purchase_a_sword():
    purchase_sword_event = {'event_type': 'purchase_sword'}
    log_to_kafka('events', purchase_sword_event)
    return "Sword Purchased!\n"

@app.route("/purchase_a_shield")
def purchase_a_shield():
    purchase_shield_event = {'event_type': 'purchase_shield'}
    log_to_kafka('events', purchase_shield_event)
    return "Shield Purchased!\n"

@app.route("/join_a_guild")
def join_a_guild():
    join_guild_event = {'event_type': 'join_guild'}
    log_to_kafka('events', join_guild_event)
    return "You Have Joined A Guild!\n"
```
**docker run -it --rm -v /home/science/w205:/w205 midsw205/base:latest bash**

Next I created a docker container to change the game_api.py file. If I vi a .py file directly in the droplet, the file would be read-only. Entering the midsw205 image to create a .py file will grant me write access. -it makes it an interactive terminal, --rm makes it so that the container is removed when exited, -v mounts the local drives to the container.

**cd assignment-11-adamcy99/**

I need to navigate to the directory where I want to change the game_api.py file.

**vi game_api.py**

Now I will make some changes to the game_api.py file. I added purchase_a_shiled and join_a_guild event functions to the code. The final version of the code is shown below:

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
    return "This is the default response!\n"


@app.route("/purchase_a_sword")
def purchase_a_sword():
    purchase_sword_event = {'event_type': 'purchase_sword'}
    log_to_kafka('events', purchase_sword_event)
    return "Sword Purchased!\n"

@app.route("/purchase_a_shield")
def purchase_a_shield():
    purchase_shield_event = {'event_type': 'purchase_shield'}
    log_to_kafka('events', purchase_shield_event)
    return "Shield Purchased!\n"

@app.route("/join_a_guild")
def join_a_guild():
    join_guild_event = {'event_type': 'join_guild'}
    log_to_kafka('events', join_guild_event)
    return "You Have Joined A Guild!\n"
```
In the first few lines of the code, we are importing the json library, the KafkaProducer class from the python kafka module, and the Flask class from the flask module. Then we created a Flask object called app which is how we build our web application. We also created a KafkaProducer object called producer which we initialize by telling it to connect to kafka through the 29092 port. Then we created a function called log_to_kafka which will send the events we create into our kafka topic through the producer object. There is a line there called event.update(request.headers). This line of code is taking the dictionary events we wrote in the form of {‘event_type’: default_event} and adding headers to it that includes the host IP among other things before publishing it to kafka. Then we used the route decorator maker with our app object to add a url rule for our default_response(), purchase_a_sword(), join_a_guild(), and purchase_a_shield() functions. In each of the functions, we create an a dictionary object. For example, in the purchase_a_sword() function, we created the purchase_a_sword_event dictionary object that has "event_type" as a key, and "purchase_sword" as the value. Then we run our log_to_kafka() function, where we will pass our purchase_a_sword_event (dictionary object) into a kafka topic that we will name "events". Then we will return a "Sword Purchased" output to the command line each time we make a web API call to purchase a sword.

**exit**

Now we will exit our midsw205 container.

**docker-compose up -d**

Now I am starting up the cluster.

**docker-compose exec kafka kafka-topics --create --topic events --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181**

Here I am creating a kafka topic called "events". docker-compose exec kafka means run the command in a container. The other lines are pretty straight forward, we are creating a kafka-topic called "tests" with 1 partition, we are pairing kafka with zookeeper through the 32181 port so that zookeeper can manage kafka, etc. We get the output: ‘Created topic "events".’ When our kafka topic is created.

**docker-compose exec mids env FLASK_APP=/w205/assignment-12-adamcy99/game_api.py flask run --host 0.0.0.0**

This command runs the python flask script in the mids container of our docker cluster.  We will be able to see the outputs of our python program on the command line here as we make the web API calls.

**Open a new window and navigate to w205/assignment-12-adamcy99/**

Now, we will open a new window and navigate to the same directory.

**docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning**

Now we will use the kafkacat utility to consume the messages that our web service wrote to the kafka "events" topic. We left out the -e this time which means we do not end kafkacat and instead will have it running continuously.

**Open a new window and navigate to w205/assignment-12-adamcy99/**

Now, we will open another new window and navigate to the same directory. In this new window we will be use the Apache Bench utility to generate multiple requests of our actions. Apache Bench is designed to stress test web servers using a high volume of data in a short amount of time. 

**docker-compose exec mids ab -n 10 -H "Host: user1.comcast.com" http://localhost:5000/**

The code above uses Apache Bench to make 10 requests of the default API call from the comcast host.

**docker-compose exec mids ab -n 10 -H "Host: user1.comcast.com" http://localhost:5000/purchase_a_sword**

The code above uses Apache Bench to make 10 requests of the purchase sword API call from the comcast host.

**docker-compose exec mids ab -n 10 -H "Host: user2.att.com" http://localhost:5000/purchase_a_shield**

The code above uses Apache Bench to make 10 requests of the purchase sword API call from the att host.

**docker-compose exec mids ab -n 10 -H "Host: user2.att.com" http://localhost:5000/join_a_guild**

The code above uses Apache Bench to make 10 requests of the join guild API call from the att host.

In our spark window, we have 10 instances of each of these lines:

```
127.0.0.1 - - [02/Aug/2018 04:13:14] "GET / HTTP/1.0" 200 -

127.0.0.1 - - [02/Aug/2018 04:13:19] "GET /purchase_a_sword HTTP/1.0" 200 -

127.0.0.1 - - [02/Aug/2018 04:13:27] "GET /purchase_a_shield HTTP/1.0" 200 -

127.0.0.1 - - [02/Aug/2018 04:13:34] "GET /join_a_guild HTTP/1.0" 200 -
```

In our kafkacat window, we have instances of each of these lines:

```
{"Host": "user1.comcast.com", "event_type": "default", "Accept": "*/*", "User-Agent": "ApacheBench/2.3"}

{"Host": "user1.comcast.com", "event_type": "purchase_sword", "Accept": "*/*", "User-Agent": "ApacheBench/2.3"}

{"Host": "user2.att.com", "event_type": "purchase_shield", "Accept": "*/*", "User-Agent": "ApacheBench/2.3"}

{"Host": "user2.att.com", "event_type": "join_guild", "Accept": "*/*", "User-Agent": "ApacheBench/2.3"}
```

**vi ~/w205/assignment-11-adamcy99/separate_events.py**

First we will take a look at the spark code using python that we wrote last week:

```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf


@udf('string')
def munge_event(event_as_json):
    event = json.loads(event_as_json)
    event['Host'] = "moe"
    event['Cache-Control'] = "no-cache"
    return json.dumps(event)


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .getOrCreate()

    raw_events = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()

    munged_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),
                raw_events.timestamp.cast('string')) \
        .withColumn('munged', munge_event('raw'))

    extracted_events = munged_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.munged))) \
        .toDF()

    sword_purchases = extracted_events \
        .filter(extracted_events.event_type == 'purchase_sword')
    sword_purchases.show()
    # sword_purchases \
        # .write \
        # .mode("overwrite") \
        # .parquet("/tmp/sword_purchases")

    default_hits = extracted_events \
        .filter(extracted_events.event_type == 'default')
    default_hits.show()
    # default_hits \
        # .write \
        # .mode("overwrite") \
        # .parquet("/tmp/default_hits")

    shield_purchases = extracted_events \
        .filter(extracted_events.event_type == 'purchase_shield')
    shield_purchases.show()
    # shield_purchases \
        # .write \
        # .mode("overwrite") \
        # .parquet("/tmp/default_hits")

    guilds_joined = extracted_events \
        .filter(extracted_events.event_type == 'join_guild')
    guilds_joined.show()
    # guilds_joined \
        # .write \
        # .mode("overwrite") \
        # .parquet("/tmp/default_hits")

if __name__ == "__main__":
    main()
```

This code enables us to separate our different events. For example, our sword purchase events will be separated from our shield purchase events. In this code, we simply create 4 data frames, one called sword_purchases that only stores sword purchase events, one called default_hits that only store default events, etc. It should be noted that this code can only handle 1 schema for events and would break if we gave it 2 different schemas for events. Notice how we had to write in code for purchase_shield and join_guild for them to work.

**docker-compose exec spark spark-submit /w205/assignment-11-adamcy99/separate_events.py**

Now we will use spark-submit to run our code to see what we get. We will see 4 different data frames, one for each of our event types.

**vi just_filtering.py**

Now lets take a look at the just_filtering.py code that will allow us to accept multiple schemas:

```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf


@udf('boolean')
def is_purchase(event_as_json):
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_sword':
        return True
    return False


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .getOrCreate()

    raw_events = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()

    purchase_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),
                raw_events.timestamp.cast('string')) \
        .filter(is_purchase('raw'))

    extracted_purchase_events = purchase_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.raw))) \
        .toDF()
    extracted_purchase_events.printSchema()
    extracted_purchase_events.show()


if __name__ == "__main__":
    main()

```

**docker-compose exec spark spark-submit /w205/assignment-12-adamcy99/just_filtering.py**

Now we can handle more than 1 kind of schema. However, the code provided only filters out and gives us the purchase_sword events.

**vi filtered_writes.py**

Now we will take a look at the filtered_writes.py code that uses massively parallel processing to write to hadoop hdfs in parquet format. There is an overwrite option in this code that allows us to write into directories that already existed. We can therefore read it back in quickly if it’s a large data set.

```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf


@udf('boolean')
def is_purchase(event_as_json):
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_sword':
        return True
    return False


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .getOrCreate()

    raw_events = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()

    purchase_events = raw_events \
        .select(raw_events.value.cast('string').alias('raw'),
                raw_events.timestamp.cast('string')) \
        .filter(is_purchase('raw'))

    extracted_purchase_events = purchase_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.raw))) \
        .toDF()
    extracted_purchase_events.printSchema()
    extracted_purchase_events.show()

    extracted_purchase_events \
        .write \
        .mode('overwrite') \
        .parquet('/tmp/purchases')


if __name__ == "__main__":
    main()
```

**docker-compose exec spark spark-submit /w205/assignment-12-adamcy99/filtered_writes.py**

Now we will use the spark-submit utility to run the code.

**docker-compose exec cloudera hadoop fs -ls /tmp/**

**docker-compose exec cloudera hadoop fs -ls /tmp/purchases/**

Now we will check our hadoop hdfs to see our files. We see our purchases directory, and inside we see the _SUCCESS file and the parquet file.

**docker-compose exec spark env PYSPARK_DRIVER_PYTHON=jupyter PYSPARK_DRIVER_PYTHON_OPTS='notebook --no-browser --port 8888 --ip 0.0.0.0 --allow-root' pyspark**

Now we will startup a jupyter notebook. We get the following token: http://0.0.0.0:8888/?token=33aeeba17e60995aa0b8942a0ff9a21c26735576632b273d. We must replace the 0.0.0.0 with our droplet IP address. Then we paste that into a browser and we will get our Jupyter Notebook.

**In Jupyter Notebook, run each of the following lines:**

```python
purchases = spark.read.parquet('/tmp/purchases')
purchases.show()
purchases.registerTempTable('purchases')
purchases_by_example2 = spark.sql("select * from purchases where Host = 'user1.comcast.com'")
purchases_by_example2.show()
df = purchases_by_example2.toPandas()
df.describe()
```
We are performing a massively parallel read from our hadoop hdfs. Then we are showing the read in data frame. Then we can query using spark.sql and return a spark df with our query. Then we print out that spark data frame.  Then we convert the spark data frame to a pandas data frame.

**docker-compose down**

Now we can tear down our cluster.

### Appendix:

1. I created functions to join_a_guild and purchase_a_shield in the game_api.py file.

2. With Apache Bench, i ran the default function with comcast, purchase_a_sword with comcast, join_a_guild with att, and purchase_a_shield with att so we can see them all when we use kafkacat.

3. I modified the separate_events.py file so that it would separate join guild and purchase shield events as well.



