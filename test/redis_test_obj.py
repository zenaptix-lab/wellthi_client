from Models.RedisConf import *

if __name__ == '__main__':
    red = RedisConf(host='localhost', port=6379, db=0)
    red.subscribe('stressed_event')