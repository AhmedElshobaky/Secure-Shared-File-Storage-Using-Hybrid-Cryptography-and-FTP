from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, DES, Blowfish, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import os
import client


class Encryption:
    def __init__(self, file_path, key_path, master_key_path=None):
        self.N = 0
        self.key_list = []
        self.chunks = []
        self.file_path = file_path
        self.file_size = 0
        self.ciphers = ["AES", "DES", "Blowfish"]
        self.encrypted_file = []
        self.encrypted_master_key = None
        self.key_path = key_path
        self.RSA_key = None
        self.master_key_path = master_key_path
        self.master_key = None
        self.ftp_client = client.FTPClient()
        self.decrypted_file = []

    def generate_key(self, cipher_type):
        password = b"CSE451 - Computer and Network Security"
        # DES key is of length 8 bytes --> 64 bits
        if cipher_type == "DES":
            salt = get_random_bytes(8)
            key = PBKDF2(password, salt, dkLen=8)
            self.key_list.append(key)
        # both AES and Blowfish keys are of length 16 bytes --> 128 bits
        else:
            salt = get_random_bytes(16)
            key = PBKDF2(password, salt, dkLen=16)
            self.key_list.append(key)
        return

    def padding_file(self):
        # get file size
        self.file_size = os.path.getsize(self.file_path)
        # get the size of the last chunk
        last_chunk_size = self.file_size % 128
        print("DEBUG padding_file last_chunk_size: " + str(last_chunk_size))
        # get the padding size
        if not last_chunk_size == 0:
            padding_size = 128 - last_chunk_size
            # get the padding
            padding = b" " * padding_size
            # add the padding to the last chunk
            with open(self.file_path, "ab") as f:
                f.write(padding)
        return

    def divide_file(self):
        # padding logic for the last chunk
        self.padding_file()
        # get file size
        self.file_size = os.path.getsize(self.file_path)
        # get the number of parts
        num_parts = self.file_size // 128
        print("DEBUG divide_file num_parts: " + str(num_parts))
        # divide the file into N parts of 128 bytes if i
        with open(self.file_path, "rb") as f:
            for i in range(num_parts):
                if i % 3 == 0:
                    chunk = f.read(128)
                else:
                    chunk = f.read(64)
                self.chunks.append(chunk)
        return

    def get_keys(self):
        # generate keys
        for cipher in self.ciphers:
            self.generate_key(cipher)
        print("DEBUG get_keys key_list: " + str(self.key_list))
        return

    def encrypt_file(self):
        # encrypt the file
        for i in range(len(self.chunks)):
            # if i % 3: encrept with AES
            # if i % 3 == 1: encrypt with DES
            # if i % 3 == 2: encrypt with Blowfish
            if i % 3 == 0:
                cipher = AES.new(self.key_list[0], AES.MODE_ECB)
            elif i % 3 == 1:
                cipher = DES.new(self.key_list[1], DES.MODE_ECB)
            elif i % 3 == 2:
                cipher = Blowfish.new(self.key_list[2], Blowfish.MODE_ECB)

            print()
            ciphertext = cipher.encrypt(self.chunks[i])
            print(
                "DEBUG encrypt_file ciphertext: "
                + str(self.ciphers[i % 3])
                + " "
                + str(ciphertext)
            )
            self.encrypted_file.append(ciphertext)

        return

    # encrypt the keys with the public key
    def encrypt_keys(self):
        with open(self.key_path, "rb") as f:
            RSA_key = f.read()
            self.RSA_key = RSA.import_key(RSA_key)
        cipher = PKCS1_OAEP.new(self.RSA_key)

        print(b"".join(self.key_list))

        with open(f'{self.file_path.split("/")[-1]}.key', "wb") as f:
            f.write(b"".join(self.key_list))

        self.encrypted_master_key = cipher.encrypt(b"".join(self.key_list))
        print(
            "DEBUG encrypt_keys encrypted_master_key: " + str(self.encrypted_master_key)
        )
        return

    def upload_file(self):

        # gets generated keys
        self.get_keys()
        # encrypt the keys
        self.encrypt_keys()
        # divide the file into N parts
        self.divide_file()
        # encrypt the file
        self.encrypt_file()

        # upload the file

        with open(f'{self.file_path.split("/")[-1]}.enc', "wb") as f:
            f.write(b"".join(self.encrypted_file))

        with open(f'{self.file_path.split("/")[-1]}.key.enc', "wb") as f:
            f.write(self.encrypted_master_key)

        self.ftp_client.upload_file(f'{self.file_path.split("/")[-1]}.enc')
        self.ftp_client.upload_file(f'{self.file_path.split("/")[-1]}.key.enc')
        os.remove(f'{self.file_path.split("/")[-1]}.enc')
        os.remove(f'{self.file_path.split("/")[-1]}.key.enc')

    def download_file(self):
        # download the file
        # get test.txt.key.enc
        # get private key of the user
        # decrypt key.enc with public key of the user --> key
        # decrypt file.enc with key

        # download the file
        currdir = os.getcwd()
        if not os.path.exists(os.path.join(currdir, "downloads")):
            os.mkdir(os.path.join(currdir, "downloads"))

        download_dir = os.path.join(currdir, "downloads")
        os.chdir(download_dir)

        self.ftp_client.download_file(f"{self.file_path}")

        with open(self.master_key_path, "rb") as f:
            self.master_key = f.read()

        with open(self.key_path, "rb") as f:
            RSA_key = f.read()
            self.RSA_key = RSA.import_key(RSA_key)
        cipher = PKCS1_OAEP.new(self.RSA_key)

        print(self.master_key)
        decrypted_master_key = cipher.decrypt(self.master_key)
        print("DEBUG download_file decrypted_master_key: " + str(decrypted_master_key))

        # divide the file into N parts
        # get file size
        self.file_size = os.path.getsize(self.file_path)
        # get the number of parts
        num_parts = self.file_size // 128
        with open(self.file_path, "rb") as f:
            for i in range(num_parts):
                if i % 3 == 0:
                    chunk = f.read(128)
                else:
                    chunk = f.read(64)
                self.chunks.append(chunk)

        # decrypt the file
        AES_key = decrypted_master_key[:16]
        DES_key = decrypted_master_key[16:24]
        Blowfish_key = decrypted_master_key[24:]
        for i in range(len(self.chunks)):
            # if i % 3: encrept with AES
            # if i % 3 == 1: encrypt with DES
            # if i % 3 == 2: encrypt with Blowfish
            if i % 3 == 0:
                cipher = AES.new(AES_key, AES.MODE_ECB)
            elif i % 3 == 1:
                cipher = DES.new(DES_key, DES.MODE_ECB)
            elif i % 3 == 2:
                cipher = Blowfish.new(Blowfish_key, Blowfish.MODE_ECB)
            print()
            ciphertext = cipher.decrypt(self.chunks[i])
            print(
                "DEBUG encrypt_file ciphertext: "
                + str(self.ciphers[i % 3])
                + " "
                + str(ciphertext)
            )
            self.decrypted_file.append(ciphertext)
        print("DEBUG download_file decrypted_file: " + str(self.decrypted_file))
        # write the file
        with open(f"{self.file_path}.dec", "wb") as f:
            f.write(b"".join(self.decrypted_file).replace(b" ", b""))
        os.chdir(currdir)
        return
