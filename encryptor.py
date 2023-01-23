from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def encrypt_file(filename: str, key: bytes) -> None:
    # Read the contents of the file into memory
    with open(filename, "rb") as file:
        plaintext = file.read()

    cipher = PKCS1_OAEP.new(RSA.import_key(key))

    # Write the encrypted data to a new file
    with open(f"{filename}.enc", "wb") as file:
        file.write(cipher.encrypt(plaintext))


def main() -> None:
    # Read the filename and key from the command line arguments
    filename = "test.txt.key"
    with open("keys/public_key_user.pem", "rb") as f:
        key = f.read()

    # Encrypt the file
    encrypt_file(filename, key)


if __name__ == "__main__":
    main()
