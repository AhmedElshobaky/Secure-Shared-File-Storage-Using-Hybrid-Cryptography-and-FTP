import tkinter as tk
from tkinter import filedialog, ttk
import server
import client
import encryption as enc

class FileSharingApp(tk.Tk):
    def __init__(self):
        self.ftp_client = client.FTPClient()
        tk.Tk.__init__(self)
        self.title("Secure File Sharing App")
        self.geometry("700x500")
        self.key_path = None
        self.master_key = None
        
        #list of files on the server
        self.file_list = tk.Listbox(self, height= 20, width= 60, border= 0)
        self.file_list.pack()
        choose_key_button = tk.Button(self, text="Choose a key", command=self.choose_key_button)
        choose_key_button.pack()
        
        upload_button = tk.Button(self, text="Upload File", command=self.upload_file)
        upload_button.pack()
        
        download_button = tk.Button(self, text="Download File", command=self.download_file)
        download_button.pack()
        view_button = tk.Button(self, text="View Files", command=self.view_files)
        view_button.pack()

        delete_button = tk.Button(self, text="Delete File", command=self.delete_file)
        delete_button.pack()

        self.view_files()
    
    def choose_key_button(self):
        filepath = filedialog.askopenfilename()
        print("DEBUG choose_key_button filepath: ", filepath)
        if filepath == "":
            print("No file selected")
            return
        self.key_path = filepath
        print("Key has been chosen")

    def upload_file(self):
        if self.key_path is None:
            #TODO: add a pop-up window
            print("No key selected")
            return
        filepath = filedialog.askopenfilename()
        print("DEBUG upload_file filepath: ", filepath)
        if filepath == "":
            print("No file selected")
            return
        self.encryption(filepath, True)
        self.view_files()
        
    def download_file(self):
        filepath = self.file_list.get(tk.ACTIVE)
        print("DEBUG download_file filepath: ", filepath)
        if filepath == "":
            print("No file selected")
            return
        print("Please choose a master key")
        master_key = filedialog.askopenfilename()
        if master_key == "":
            print("No file selected")
            return
        self.master_key = master_key

        self.encryption(filepath, False)
        print("File has been downloaded")
        
    def view_files(self):
        files = self.ftp_client.view_files()
        if files is None:
             return
        self.file_list.delete(0, tk.END)
        for file in files:
            self.file_list.insert(tk.END, file)
        print("Files on the server")
        
    def delete_file(self):
        filepath = self.file_list.get(tk.ACTIVE)
        self.ftp_client.delete_file(filepath)
        print("File has been deleted")
        self.view_files()

    

    def encryption(self, filepath, upload):
        encryptor = enc.Encryption(file_path=filepath, key_path=self.key_path, master_key_path=self.master_key)
        if upload:
            encryptor.upload_file()
            print("File has been encrypted and uploaded")
        else:
            encryptor.download_file()
            print("File has been decrypted and downloaded")


if __name__ == "__main__":
    app = FileSharingApp()
    app.mainloop()
