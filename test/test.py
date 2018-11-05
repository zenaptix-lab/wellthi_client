from Models.ChatMessages import *
import json
import watson_developer_cloud

if __name__ == '__main__':
    # assistant = watson_developer_cloud.AssistantV1(
    #     username="d01d68b2-3864-4401-a26d-92b10ef74e48",
    #     password="FUWYZmMJmjGF",
    #     version='2018-09-20')
    #
    # response = assistant.message(
    #     workspace_id='953d25b4-9170-47e5-b465-fc513f60ce1d',
    #     input={
    #         'text': 'Hello'
    #       }
    #     ).get_result()
    #
    # print(json.dumps(response, indent=2))

    response = MessageHelpers("d01d68b2-3864-4401-a26d-92b10ef74e48","FUWYZmMJmjGF",'2018-09-20').post_message('953d25b4-9170-47e5-b465-fc513f60ce1d',"Y")
    print(response)

