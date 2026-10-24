from socket import *
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import subprocess
import sys
import base64

import struct


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
    try:
        while True:
            raw = recv_msg(clientSocket)

            if raw is None:
                break

            raw_str = raw.decode("utf-8")

            if raw_str.startswith("ENC:"):
                encrypted_message = raw_str[4:]

                try:
                    decrypted_message = decrypt_message(encrypted_message)

                except ValueError:
                    send_msg(clientSocket, "ERR")
                    continue

                send_msg(clientSocket, "ACK")

            elif raw_str.startswith("RAW:"):
                message = raw_str[4:]

                send_msg(clientSocket, "ACK")

            else:
                send_msg(clientSocket, "ERR")

    except (OSError, ValueError) as e:
        print(f"Client {username} error: {e}")

    finally:
        clientSocket.close()
        print(f"{username} disconnected")            

#TODO: Decryt message function
def decrypt_message(encrypted_message_str):
    key, IV = get_key_and_IV()
    encrypted_bytes = base64.b64decode(encrypted_message_str)

    cypher = AES.new(key, AES.MODE_EAX, IV)
    decrypted_padded = cypher.decrypt(encrypted_bytes)
    decrypted_clean = unpad(decrypted_padded, AES.block_size)

    return decrypted_clean.decode("utf-8")







print("The server is ready to receive")



def send_msg(sock, msg):
    data = msg.encode("utf-8")
    header = struct.pack("!I", len(data))
    sock.sendall(header + data)

def recv_exact(sock, num_bytes):
    data = bytearray()
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            return None
        
        data.extend(chunk)
    return bytes(data)

def recv_msg(sock):
    header = recv_exact(sock, 4)
    if header is None:
        return None
    
    msg_len = struct.unpack("!I", header)[0]
    if msg_len > 1024 * 1024:
        raise ValueError("Message too long")
    return recv_exact(sock, msg_len)


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
