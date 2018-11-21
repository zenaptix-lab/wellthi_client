__author__ = 'rikus'
import requests
import json
import watson_developer_cloud
import arrow
import operator


class Watson_Config(object):
    def __init__(self, username, password, version):
        self.assistant = watson_developer_cloud.AssistantV1(
            username=username, password=password, version=version
        )
        self.chat_context = """{}"""


class MessageHelpers(Watson_Config):
    def __init__(self, username, password, version):
        Watson_Config.__init__(self, username, password, version)

    def update_watson_config(self, username, password, version):
        Watson_Config.__init__(self, username, password, version)

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
        # return response['context']
        # return json.dumps(response,indent=2)
        return response['output']['text'][0]

    @classmethod
    def time_window(self):
        today = arrow.now().format('YYYY-MM-DD')
        today_index = str(today).split("-")
        tomorrow = today_index[0] + "-" + today_index[1] + "-" + str(int(today_index[2]) + 1)
        return "response_timestamp>=" + today + "," + "response_timestamp<" + tomorrow

    @classmethod
    def get_current_chat(self, chat_server, workspace_id):
        current_chat = {}
        log_events = chat_server.assistant.list_logs(workspace_id, "-request_timestamp",
                                                     MessageHelpers.time_window())
        log_events_dic = json.loads(str(log_events))

        for chat in log_events_dic['result']['logs']:
            timestamp = chat['request_timestamp']
            request = chat['request']
            intents = chat['response']['intents']
            try:
                conversation_id = request['context']['conversation_id']
            except:
                conversation_id = ""

            if conversation_id != "":
                if conversation_id in current_chat:
                    current_chat[conversation_id].append([timestamp, request['input'], intents])

                else:
                    current_chat[conversation_id] = [timestamp, request['input'], intents]

        # return sorted(current_chat.values(), key=operator.itemgetter(0), reverse=True)
        return current_chat

class Greetings(object):
    def __init__(self):
        pass

    def post_greeting(self, url):
        json_message = """{\"input\": {\"text\": \"I am stressed\"}}"""
        response = MessageHelpers.post_message(json_message)
        return response
