__author__ = 'rikus'

import time
import redis

class RedisConf(object):
    def __init__(self, host, port=6379, db=0):
        self.r = redis.StrictRedis(host=host, port=port, db=db)
        self.p = self.r.pubsub(ignore_subscribe_messages=True)

    def my_handler(message):
        print message['data']

    def subscribe(self, events):
        # self.p.subscribe(*events)
        self.p.subscribe(**{'stressed_event': self.my_handler})
        self.p.run_in_thread(sleep_time=1)