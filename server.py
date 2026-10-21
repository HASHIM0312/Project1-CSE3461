import sys
from socket import *
import threading

PORT = 5050
HOST="" # any addresses

# lock for clients as multiple clientHandler threads touch it
clients_lock = threading.Lock()
clients:list[socket]= []

# broadcast messages from one client to all other clients
def broadcast_message(msg: bytes, sender: socket):
    # store dead/error sockets
    dead:list[socket] =[] 
    with clients_lock:
        for client in clients:
            try:
                if client is not sender:
                    client.sendall(msg)
            except OSError:
                dead.append(client)
        # remove dead connections from clients
        for client in dead:
            clients.remove(client)
            client.close()

# continuesly receive/broadcast messages from one client
def clientHandler(conn:socket):
    # record the address for staus messages
    peer = conn.getpeername()
    try:
        while True:
            data = conn.recv(1024)
            # check if disconnected
            if not data:
                break
            print(f"Received: {data.decode()} from {peer}\n")
            broadcast_message(data,conn)
    except OSError:
        pass
    finally:
        # remove a client from the list and close the connection when client disconnects
        with clients_lock:
            if conn in clients:
                clients.remove(conn)

        print(f"Client {peer} disconnected")
        conn.close()



def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    # allow immediate restart
    server_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    
    server_socket.listen()

    
    while True:
        # accept new connections
        print("Waiting for connections...")
        conn, addr = server_socket.accept()
        print(f"Connected to {conn.getpeername()}")
        # add client to the client list
        with clients_lock:
            clients.append(conn)
        # start a new thread to handle communication with the client
        threading.Thread(target = clientHandler, args =(conn,),daemon=True).start()
   

if __name__ == "__main__":
    main()

            






