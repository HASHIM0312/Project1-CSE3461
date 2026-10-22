from socket import *
import threading

serverPort = 5050
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen()
clients = {} #dictionary of clients


def accept_client_handler(clientSocket, username):
    while True:
        raw = clientSocket.recv(1024)
        if not raw:
            break

        print("Recieved payload: ", raw.decode())


#TODO: Decryt message function

#TODO: function to turn off encryption/decryption






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