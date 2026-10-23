from socket import *
import threading

serverPort = 5050
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen()
clients = {} #dictionary of clients, username => socket

def handle_client(clientSocket: socket, username):
    while True:
        try:
            data = clientSocket.recv(1024)
            if not data:
                break
            message = data.decode()
            print(username + " sent: " + message)   #recv data from user

            #checks for proper @ syntax and removes the @ char from the string
            if message.startswith("@"):
                message = message[1:] #remove @
                parts = message.split(" ", 1) # splits once at a space

                #required check just in case a user types just @user as a message with no text afterwards
                if len(parts) == 2: 
                    targetUsername = parts[0]
                    messageText = parts[1]

                    # check if user actually exists
                    if targetUsername in clients:
                        targetSocket = clients[targetUsername]
                        targetSocket.send((username + ": " + messageText).encode())
                    
                    else: clientSocket.send(("User " + targetUsername + " not found").encode())
                #improper syntax fallbacks
                else: clientSocket.send("Use format: @username message".encode())
            else: clientSocket.send("Use format: @username message".encode())
        except OSError:
            break

    # remove client on disconect
    if username in clients:
        del clients[username]
    clientSocket.close()
    print(username + " disconnected")

print("The server is ready to receive")

while True:

    #accept new TCP connection and ask for username
    clientSocket, clientAddress = serverSocket.accept()
    print("Connected to:", clientAddress)
    clientSocket.send("Enter username:".encode())

    # receive username from user
    data = clientSocket.recv(1024)
    username = data.decode()
    clients[username] = clientSocket
    print(username + " joined")

    # start a new thread for client
    clientThread = threading.Thread(target=handle_client, args=(clientSocket, username))
    clientThread.start()