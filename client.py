
import sys
from socket import *
import threading

PORT = 5050
HOST= sys.argv[1] if len(sys.argv) >1 else "127.0.0.1" # use localhost unless there's an host argument

# continuously receving and displaying messages from the server
def receive_messages(sock: socket):
    while True:
        try: 
            data = sock.recv(1024)
            if not data:
                print ("Server has shut down")
                break
            print(f"Received broadcast message: {data.decode()}")
        except OSError:
            print("Lost connection.")


def main():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    print(f"Connected to {HOST}:{PORT} from  {client_socket.getsockname()}\n")

    # sub thread to receive/display message from server
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    # repeatedly accept typed message from user and then send to server
    try:
        while True:
            message = input ("enter message to send ( or 'exit' to quit):\n")
            if message == "exit":
                break
            client_socket.sendall(message.encode('utf-8'))
    except OSError:
        print("Lost connection.")
    client_socket.close()


        
if __name__ == "__main__":
    main()

