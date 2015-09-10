#from main_server import app
from eve.auth import BasicAuth
#from main_server.config import Config

class MyBasicAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource,
                   method):
        return True
        if resource in ['products'] and method in ['POST', 'PATCH']:
            return username == 'admin' and password == Config['ADMIN_PASSWORD']
        else:
            return True
