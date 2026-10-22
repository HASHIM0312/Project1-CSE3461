import sys
from socket import *
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Cipher import _mode_eax
from Crypto.Random import get_random_bytes
import subprocess
import sys
import base64

serverPort = 5050
serverName = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
subprocess.run([sys.executable, "key_generator.py"]) # Runs key_generator

def get_key_and_IV():
    key = 0
    IV = 0
    with open("keyIV.txt", "rb") as f:
        key = f.read(32)
        IV = f.read(16)
    
    return key, IV


def encrypt_message(message):
    key, IV = get_key_and_IV()
    cypher = AES.new(key, AES.MODE_EAX, IV)
    message_bytes = message.encode('utf-8')
    padded_bytes = pad(message_bytes, AES.block_size)
    encrypted_message = cypher.encrypt(padded_bytes)
    return base64.b64encode(encrypted_message).decode('utf-8')


#TODO: Function to measure latency with/without encrytion/decryption

#TODO: Function to send a bunch of messages to latency with traffic 

def receive_messages(clientSocket: socket):
    while True:
        try:
            data = clientSocket.recv(1024)
            if not data:
                print("Server has shut down")
                break
            print("\nReceived: " + data.decode())
        except OSError:
            print("Lost connection.")
            break

def main():

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    print("Connected to:", clientSocket.getpeername())
    print("Client address:", clientSocket.getsockname())

    #server requests username here
    data = clientSocket.recv(1024)
    print(data.decode())
    username = input()

    # Send username to server
    clientSocket.send(username.encode())

    #start thread for recieving messages
    receiveThread = threading.Thread(
        target=receive_messages,
        args=(clientSocket,)
    )
    #main thread start
    receiveThread.start()
    print("Send messages using: @username message")
    while True:
        try:
            message = input(
                "Enter message to send (or 'exit' to quit):\n"
            )
            if message == "exit":
                break

            encrypt_choice = input("Encrypt message? (y/n): ")
            if encrypt_choice.lower() == 'y':
                encrypted_text = encrypt_message(message)
                to_send = "ENC:" + encrypted_text
                print(f"Encrypted message to send: {encrypted_text}")
            else:
                to_send = "RAW:" + message

            clientSocket.send(to_send.encode('utf-8'))

        except OSError:
            print("Connection lost")
            break
    clientSocket.close()

if __name__ == "__main__":
    main()