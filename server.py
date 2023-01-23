import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

class AppFTPServer:
    def __init__(self):
        # Instantiate a dummy authorizer for managing 'virtual' users
        self.authorizer = DummyAuthorizer()
        
        self.addUser('ahmed', 'password')
        self.addUser('marawan', 'password')
        # Instantiate FTP handler class
        handler = FTPHandler
        handler.authorizer = self.authorizer

        # Define a customized banner (string returned when client connects)
        handler.banner = "pyftpdlib based ftpd ready."

        # Specify a masquerade address and the range of ports to use for
        # passive connections.  Decomment in case you're behind a NAT.
        #handler.masquerade_address = '151.25.42.11'
        #handler.passive_ports = range(60000, 65535)

        # Instantiate FTP server class and listen on 0.0.0.0:2121
        address = ('0.0.0.0', 6060)
        server = FTPServer(address, handler)

        # set a limit for connections
        server.max_cons = 256
        server.max_cons_per_ip = 5

        # start ftp server
        server.serve_forever()

    def addUser(self, username, password):
        ftptemp = os.path.join(os.getcwd(), 'ftptemp')
        print('DEBUG PATH FTPTEMP:' + ftptemp)
        if not os.path.exists(ftptemp):
            os.mkdir(ftptemp)
        self.authorizer.add_user(username, password, ftptemp, perm='elradfmwMT')


if __name__ == "__main__":
    server = AppFTPServer()

