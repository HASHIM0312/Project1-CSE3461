from socket import *
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import _mode_eax
from Crypto.Random import get_random_bytes
import subprocess
import sys
import base64


serverPort = 5050
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen()
clients = {} #dictionary of clients


def get_key_and_IV():
    key = 0
    IV = 0
    with open("keyIV.txt", "rb") as f:
        key = f.read(32)
        IV = f.read(16)
    
    return key, IV


def accept_client_handler(clientSocket, username):
    while True:
        raw = clientSocket.recv(1024)
        if not raw:
            break

        raw_str = raw.decode("utf-8")
        if raw_str.startswith("ENC:"):
            encrypted_message = raw_str[4:]
            print("Recieved encrypted payload: ", encrypted_message)
            decrypted_message = decrypt_message(encrypted_message)
            print(f"Decrypted message: {decrypted_message}")
        elif raw_str.startswith("RAW:"):
            message = raw_str[4:]
            print(f"Received unencrypted message: {message}") 


#TODO: Decryt message function
def decrypt_message(encrypted_message_str):
    key, IV = get_key_and_IV()
    encrypted_bytes = base64.b64decode(encrypted_message_str)

    cypher = AES.new(key, AES.MODE_EAX, IV)
    decrypted_padded = cypher.decrypt(encrypted_bytes)
    decrypted_clean = unpad(decrypted_padded, AES.block_size)

    return decrypted_clean.decode("utf-8")







print("The server is ready to receive")




while True:

    #Accept new TCP connection and ask for username
    clientSocket, clientAddress = serverSocket.accept()
    print("Connected to:", clientAddress)
    clientSocket.send("Enter username:".encode())

    # Receive username
    data = clientSocket.recv(1024)
    username = data.decode()
    clients[username] = clientSocket
    print(username + " joined")

    # Start a new thread for client
    clientThread = threading.Thread(
        #set target to handled client when the client handler method is created
        target=accept_client_handler,
        args=(clientSocket, username)
    )
    clientThread.start()