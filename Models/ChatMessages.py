__author__ = 'rikus'
import requests
import json
import watson_developer_cloud


class Watson_Config(object):
    def __init__(self, username, password, version):
        self.assistant = watson_developer_cloud.AssistantV1(
            username=username, password=password, version=version
        )
        self.chat_context = """{}"""


class MessageHelpers(Watson_Config):
    def __init__(self, username, password, version):
        Watson_Config.__init__(self, username, password, version)

    def update_watson_config(self,username, password, version):
        Watson_Config.__init__(self, username, password, version)

    # @classmethod
    def post_message(self, workspace_id, message):
        formatted_msg = ' '.join(message.split())
        response = self.assistant.message(
            workspace_id=workspace_id,
            input={
                'text': formatted_msg
            },
            context=self.chat_context
        ).get_result()
        self.chat_context = response['context']
        #return response['context']
        #return json.dumps(response,indent=2)
        return response['output']['text'][0]


class Greetings(object):
    def __init__(self):
        pass

    def post_greeting(self, url):
        json_message = """{\"input\": {\"text\": \"I am stressed\"}}"""
        response = MessageHelpers.post_message(json_message)
        return response
