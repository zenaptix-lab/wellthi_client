__author__ = 'rikus'

import time
import redis


# class RedisConf(object):
#     def __init__(self, host, port=6379, db=0):
#         self.r = redis.StrictRedis(host=host, port=port, db=db)
#         self.p = self.r.pubsub(ignore_subscribe_messages=True)
#
#     def my_handler(message):
#         print message['data']
#
#     def subscribe(self, events):
#         # self.p.subscribe(*events)
#         self.p.subscribe(**{'stressed_event': self.my_handler})
#         self.p.run_in_thread(sleep_time=1)

class RedisConf(object):
    def __init__(self, host, port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db

    def my_handler(self, message):
        print 'MY HANDLER: ', message['data']

    def connectRedis(self, *events):
        try:
            r = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
            p = r.pubsub(ignore_subscribe_messages=True)
            for event in events:
                p.subscribe(**{event: self.my_handler})
            p.run_in_thread(sleep_time=1)
        except:
            print("Redis not connected !!!!!!!!!!!!!")
