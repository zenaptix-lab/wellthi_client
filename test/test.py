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

    chat_server = MessageHelpers("d01d68b2-3864-4401-a26d-92b10ef74e48","chat_bot_page",'2018-09-20')

    ############## chat interaction 1
    print("chat_context BEFORE POST : " , chat_server.chat_context)
    response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d',"stressed")
    print("chat_context : " , chat_server.chat_context)
    print(response)

    ############## chat interaction 2
    print("chat_context BEFORE POST2 : " , chat_server.chat_context)
    response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d',"Y")
    print("chat_context : " , chat_server.chat_context)
    print(response)

    ############## chat interaction 3
    print("chat_context BEFORE POST3 : " , chat_server.chat_context)
    response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d',"Y")
    print("chat_context : " , chat_server.chat_context)
    print(response)

    ############## chat interaction 4
    print("chat_context BEFORE POST4 : " , chat_server.chat_context)
    response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d',"3")
    print("chat_context : " , chat_server.chat_context)
    print(response)

    ############## chat interaction 5
    print("chat_context BEFORE POST5 : " , chat_server.chat_context)
    response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d',"angry")
    print("chat_context : " , chat_server.chat_context)
    print(response)


    ############## chat interaction 6
    print("chat_context BEFORE POST6 : " , chat_server.chat_context)
    response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d',"9")
    end = chat_server.chat_context['system']

    if 'branch_exited_reason' in end:
        print ("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ I have exited that chat")
    else:
        print("########################################## I am still chatting")

    print("chat_context : " , chat_server.chat_context)
    print(response)
