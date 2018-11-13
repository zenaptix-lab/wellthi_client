import redis
import time

def getMessage(p):
    while True:
        sub_message = p.get_message()
        if str(sub_message) != "None":
            if sub_message['type'] == "message":
                print(sub_message['data'])
                break
        time.sleep(5)

def my_handler(message):
    print 'MY HANDLER: ', message['data']

if __name__ == '__main__':
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set('foo', 'bar')
    result = r.get('foo')
    print(result)

    p = r.pubsub(ignore_subscribe_messages=True)

    p.subscribe(**{'stressed_event': my_handler})

    print("starting to listen")

    p.run_in_thread(sleep_time=1)
    # getMessage(p)