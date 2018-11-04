__author__ = 'rikus'
import requests
import json

class Message(object):
    def __init__(self,message):
        self.message = message

class MessageHelpers(object):
    def __init__(self):
        pass

    @classmethod
    def post_message(self,url,json_message):
        headers = {'content-type': 'application/json'}
        r = requests.post(url, headers=headers, data=json.dumps(json_message))
        return r.json()

class Greetings(object):
    def __init__(self):
        pass

    def post_greeting(self,url):
        json_message = """{\"input\": {\"text\": \"I am stressed\"}}"""
        response = MessageHelpers.post_message(url, json_message)
        return response