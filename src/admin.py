import fowardZ
from conf.config import credentials


class Admin:
    def __init__(self):
        self.user = credentials['user']
        self.password = credentials['password']
        self.token = None

    def auth(self):
        result = fowardZ.sendToZabbix(method='user.login', params={'user': self.user,
                                                                   'password': self.password})
        #print 'Admin login result: ',result
        self.token = result['result']

    def getToken(self):
        return self.token





