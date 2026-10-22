import sys
from socket import *
import threading

serverPort = 5050
serverName = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

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
            clientSocket.send(message.encode())

        except OSError:
            print("Connection lost")
            break
    clientSocket.close()

if __name__ == "__main__":
    main()