__author__ = 'rikus'
from flask import request
from ChatMessages import MessageHelpers
from watson_developer_cloud import *


class Credentials(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def update(self, username_new, password_new):
        self.username = username_new
        self.password = password_new

    def check_password(self, chat_server):
        try:
            response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d', "sdfgdfsg")
            return "valid"
        except WatsonApiException:
            return "not valid"
