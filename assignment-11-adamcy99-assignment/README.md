# Assignment 11

### Introduction

In this assignment, we will set up a web server that runs a simple web API service that simulates a mobile game where the user can perform actions such as *purchase a sword* or *join a guild*. Our web API service will allow us to use the curl utility to make API calls as well as write these calls to a kafka topic which we can view with the kafkacat utility. The messages sent to kafka will be in dictionary (key-value) format so that we can easily convert it to json later. The dictionary format would look like {"event_type": "purchase_sword"}. We also included some extensions to our printed messages to include other header information such as the host IP among other things. We have 3 other python codes: extract_events.py which will extract our events and write them to parquet in hdfs, transform_events.py while will allow us to transform parts of our event, and separate_events.py which will allow us to separate our event types into separate data frames.

### Commands and Annotations 

**cd w205/assignment-11-adamcy99/**

I first navigated to the assignment directory where I will be working in.

**sudo cp ~/w205/course-content/11-Storing-Data-III/docker-compose.yml .**

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
    expose:
      - "8888"
    ports:
      - "8888:8888"
    volumes:
      - "~/w205:/w205"
    command: bash
    depends_on:
      - cloudera
    environment:
      HADOOP_NAMENODE: cloudera
    extra_hosts:
      - "moby:127.0.0.1"

  mids:
    image: midsw205/base:latest
    stdin_open: true
    tty: true
    expose:
      - "5000"
    ports:
      - "5000:5000"
    volumes:
      - "~/w205:/w205"
    extra_hosts:
      - "moby:127.0.0.1"
```

In this file, we create a docker cluster with 5 containers: zookeeper, kafka, mids, cloudera, and spark. In the cluster, there is a virtual network that connects the containers together and allow them to communicate. For example, zookeeper and kafka are communicating through the TCP/IP port 32181 so that zookeeper can be used to manage kafka. The TCP port 5000 is the port we will use to make the API calls later on. The zookeeper, kafka, cloudera, and spark containers are off the shelf and all customization are done in the mids container. That means the only container we would maintain is the mids container. Under each container, we have "expose" parameters where we listed the ports that allow each container to communicate with the droplet virtual machine. Each of these containers are independent and stand-alone but can communicate with each other as well as share files using certain mounts that we can assign.

**sudo cp ~/w205/course-content/11-Storing-Data-III/*.py .**

Now we used the above command to copy all the .py files from the course-content/11-Storing-Data-III directory. These 4 files are: game_api.py, extract_events.py, transform_events.py, separate_events.py.

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

**docker-compose exec mids env FLASK_APP=/w205/assignment-11-adamcy99/game_api.py flask run --host 0.0.0.0**

This command runs the python flask script in the mids container of our docker cluster.  We will be able to see the outputs of our python program on the command line here as we make the web API calls.

**Open a new window and navigate to w205/assignment-11-adamcy99/**

Now, we can open a new window and navigate to the same directory. We will use the curl utility to make web API calls.

**docker-compose exec mids curl http://localhost:5000/**

Here we are making an API call with curl. As mentioned before, we are using the TCP port 5000 to make the API call. In this case we are not specifying a function such as purchase sword, or join guild. Therefore, when we run this command, we get the output "This is the default response!". In our other window where we are running the python flask API server, we get the output "127.0.0.1 - - [26/Jul/2018 19:56:47] "GET / HTTP/1.1" 200 -". Here, we see the IP address of our host server, a time stamp, and our GET command. We also see HTTP/1.1 which is stays connected after the call while HTTP/1.0 hangs up.

**docker-compose exec mids curl http://localhost:5000/purchase_a_sword**

Now we are making another API call with curl, but this time we are using the purchase_a_sword function. We get the "Sword Purchased!" response, while in the other window where we are running the python flask API server, we get the output "127.0.0.1 - - [26/Jul/2018 19:56:54] "GET /purchase_a_sword HTTP/1.1" 200 -" IT is similar to before except we can see now that we are purchasing a sword.

**docker-compose exec mids curl http://localhost:5000/join_a_guild**

Similar to the previous two commands, except now we are making an API call with curl and using the join_a_guild function. We get the output "You Have Joined A Guild!" and in our other window where we are running the python flask API server, we get the output "127.0.0.1 - - [26/Jul/2018 19:57:00] "GET /join_a_guild HTTP/1.1" 200 -". 

**docker-compose exec mids curl http://localhost:5000/purchase_a_shield**

Similar to the previous commands, except now we are making an API call with curl and using the purchase_a_shield function. We get the output "Shield Purchased!" and in our other window where we are running the python flask API server, we get the output "127.0.0.1 - - [26/Jul/2018 19:57:06] "GET /purchase_a_shield HTTP/1.1" 200 -". 

**docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning -e**

Now we will use the kafkacat utility to consume the messages that our web service wrote to the kafka "events" topic. Our kafka topic has the following messages:

{"Host": "localhost:5000", "event_type": "default", "Accept": "*/*", "User-Agent": "curl/7.47.0"}

{"Host": "localhost:5000", "event_type": "purchase_sword", "Accept": "*/*", "User-Agent": "curl/7.47.0"}

{"Host": "localhost:5000", "event_type": "join_guild", "Accept": "*/*", "User-Agent": "curl/7.47.0"}

{"Host": "localhost:5000", "event_type": "purchase_shield", "Accept": "*/*", "User-Agent": "curl/7.47.0"}

As you can see, these are the dictionary objects that we created in our game_api.py code.

**vi extract_events.py**

Now we will use the extract_events.py script to extract our kafka events and write them into hdfs. The code of the script looks like the following:

```python
#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession


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

    events = raw_events.select(raw_events.value.cast('string'))
    extracted_events = events.rdd.map(lambda x: json.loads(x.value)).toDF()

    extracted_events \
        .write \
        .parquet("/tmp/extracted_events")


if __name__ == "__main__":
    main()
```

In the code above, we are using a SparkSession object to use spark to read in our raw events from kafka. Then we store all the events into the events data frame (excluding the key values). Next, we use a massively parallel map function to extract our values from the events data frame into individual json objects. Then this data frame will be written to parquet and we will be able to see it in hdfs.

**docker-compose exec spark spark-submit /w205/assignment-11-adamcy99/extract_events.py**

Now we will use spark-submit to submit our extract_events.py file to spark and run the code.

**docker-compose exec cloudera hadoop fs -ls /tmp/**

Now we will use the cloudera container to take a look at what’s inside our hdfs. We now can see the /tmp/extracted_events directory in our hdfs.

**docker-compose exec cloudera hadoop fs -ls /tmp/extracted_events/**

When we look inside the extracted_events directory in our hdfs, we can see a SUCESS file and a parquet file.

Note that the command we used:

```docker-compose exec spark spark-submit filename.py```

is short for 

```
docker-compose exec spark \
  spark-submit \
    --master 'local[*]' \
    filename.py
```

We are not really running a cluster but rather a spark “pseudo-distributed” cluster. If we run a standalone cluster with a master node and worker nodes, we would have to use the following code to be more specific:

```
docker-compose exec spark \
  spark-submit \
    --master spark://23.195.26.187:7077 \
    filename.py
```

If we were running our spark inside of a hadoop cluster, we would have to submit to yarn instead:

```
docker-compose exec spark \
  spark-submit \
    --master yarn \
    --deploy-mode cluster \
    filename.py
```

If we were running our spark inside of a mess cluster, we would need to submit to memos master:

```
docker-compose exec spark \
  spark-submit \
    --master mesos://mesos-master:7077 \
    --deploy-mode cluster \
    filename.py
```

Finally, if we were running our spark side of a kubernetes cluster, we would need to submit to kubernetes master:

```
docker-compose exec spark \
  spark-submit \
    --master k8s://kubernetes-master:443 \
    --deploy-mode cluster \
    filename.py
```

**vi transform_events.py**

The transform_events.py code will demonstrate how we can perform transforms on our kafka events:

```python
#!/usr/bin/env python
"""Extract events from kafka, transform, and write to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf


@udf('string')
def munge_event(event_as_json):
    event = json.loads(event_as_json)
    event['Host'] = "moe" # silly change to show it works
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
    munged_events.show()

    extracted_events = munged_events \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, **json.loads(r.munged))) \
        .toDF()
    extracted_events.show()

    extracted_events \
        .write \
        .mode("overwrite") \
        .parquet("/tmp/extracted_events")


if __name__ == "__main__":
    main()
```

Here, we have a function called munge_event() where we set the ‘host’ value of our events to “moe”. Then, instead of making an “events” data frame from “raw_events”, we are making a “munged_events” data frame where we call the munge_event function transform each event.

**docker-compose exec spark spark-submit /w205/assignment-11-adamcy99/transform_events.py**

Now we will use spark-submit again to view the results. We see our events in the form of a data frame, except all of the Host values are now set to “moe”.

|Accept|Cache-Control|Host| User-Agent|     event_type|           timestamp|
|:----:|:-----------:|:--:|:---------:|:-------------:|:------------------:|
|   */*|     no-cache| moe|curl/7.47.0|        default|2018-07-26 19:56:...|
|   */*|     no-cache| moe|curl/7.47.0| purchase_sword|2018-07-26 19:56:...|
|   */*|     no-cache| moe|curl/7.47.0|     join_guild|2018-07-26 19:57:...|
|   */*|     no-cache| moe|curl/7.47.0|purchase_shield|2018-07-26 19:57:...|

**vi separate_events.py**

This code will enable us to separate our different events. For example, our sword purchase events will be separated from our shield purchase events.

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
    event['Host'] = "moe" # silly change to show it works
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


if __name__ == "__main__":
    main()
```

In this code, we simply create 4 data frames, one called sword_purchases that only stores sword purchase events, one called default_hits that only store default events, etc.

**docker-compose exec spark spark-submit /w205/assignment-11-adamcy99/separate_events.py**

Now we will use spark-submit to run our code to see what we get. We will see 4 different data frames, one for each of our event types.

**docker-compose down**

Now we can tear down our cluster.

### Appendix:

1. I created functions to join_a_guild and purchase_a_shield in the game_api.py file.

2. I ran all of the functions including the default function, purchase_a_sword, join_a_guild, and purchase_a_shield so we can see them all when we use kafkacat.

3. I modified the separate_events.py file so that it would separate join guild and purchase shield events as well.


