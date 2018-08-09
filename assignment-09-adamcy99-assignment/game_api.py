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
    return "\nShield Purchased!\n"




