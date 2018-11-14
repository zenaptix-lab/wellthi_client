__author__ = 'rikus'

import time
import redis
from flask import render_template, make_response
import requests
import json

class RedisConf(object):
    def __init__(self, host, port=6379, db=0):
        self.events = []
        self.host = host
        self.port = port
        self.db = db

    def my_handler(self, message):
        message_data = str(message['data']).lower()
        print 'MY HANDLER: ', message_data
        if "stressed" in message_data:
            print 'MY HANDLER inside : ', message_data
            self.events.append(message_data)

    def connectRedis(self, events):
        try:
            r = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
            p = r.pubsub(ignore_subscribe_messages=True)
            for event in events:
                p.subscribe(**{event: self.my_handler})
            p.run_in_thread(sleep_time=1)
        except:
            print("Redis not connected !!!!!!!!!!!!!")
