#!/usr/bin/python
import ftplib
import os

# constants
FTP_HOST = "127.0.0.1"
FTP_PORT = 6060
FTP_USER = "ahmed"
FTP_PASS = "password"
isOwner = False

class FTPClient:

    def __init__(self, host=FTP_HOST, port=FTP_PORT, user=FTP_USER, password=FTP_PASS):
        self.user = user
        self.server = ftplib.FTP()
        self.server.connect(FTP_HOST, FTP_PORT)
        self.server.login(user, password)
        print('DEBUG `__init__` PATH SERVER_DIR:' + self.server.pwd())
        self.client_dir = os.path.join(self.server.pwd(), self.user)
        print('DEBUG `__init__` PATH CLIENT_DIR:' +self.client_dir)
        print('DEBUG `__init__` SERVER DIR LIST:' + str(self.server.nlst()))
        if(self.user not in self.server.nlst()):
            self.server.mkd(self.client_dir)
            print(f'Directory {self.client_dir} has been created on the server.')
        self.server.cwd(self.client_dir)
        self.downloads_dir()
        print("Connected to the server.")

    def downloads_dir(self):
        downloads = os.path.join(os.getcwd(), 'downloads')
        if not os.path.exists(downloads):
            os.mkdir(downloads)
            print(f"Directory /downloads has been created locally.")


    def upload_file(self, file_path):
        abs_file = os.path.split(file_path)[1]
        with open(file_path, "rb") as f:
            self.server.storbinary(f'STOR {abs_file}', f, 1024)
            pass
        print(f"File {abs_file} has been uploaded to the server.")

    def download_file(self, file_path):
        
        abs_file = os.path.split(file_path)[1]
        with open(file_path, "wb") as f:
            self.server.retrbinary(f'RETR {abs_file}' , f.write, 1024)
        print(f"File {file_path} has been downloaded from the server.")
        
    def delete_file(self, file_path):
        self.server.delete(file_path)
        print(f"File {file_path} has been deleted from the server.")
        
    def view_files(self):
        files = self.server.nlst()
        return files
<<<<<<< HEAD
=======
    
        
    def close_connection(self):
        self.server.quit()
>>>>>>> 7424a06558719c83b81533ec35d7c33e7a9b2a49

