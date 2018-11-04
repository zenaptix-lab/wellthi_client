__author__ = 'rikus'

class Credentials(object):
    def __init__(self,username, password):
        self.username = username
        self.password = password

    def update(self,username_new,password_new):
        self.username = username_new
        self.password = password_new