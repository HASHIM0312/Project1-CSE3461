import sys
from socket import *
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import sys
import base64

# for testing latency of encrypted / unencrypted messages.
import time
import statistics
import struct

import client

serverPort = 5050
serverName = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

# fix: having key_generator run every time client starts,
# a new AES key is generated. When second client connects,
# it will overwrite the file and then the first client will
# not be correctly decrypted. So, must run key_gen before
# running client or server.

#subprocess.run([sys.executable, "key_generator.py"]) # Runs key_generator

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


# tests for client side overhead from encryption
def benchmark(iterations=10000):

    msgs = [
            # strings of diff lengths
                "A", "A" * 16, "A" * 1024, "A" * 4096, "A" * 128, 
            # 128 random characters
            "qu4xpIZWvgRsWNrizWkNcbL3zATmMcVFv7j7mynMXY8GibK704hOiuCerONOX7ROEEt7GabV0S0Kwdo5XMrZ2WutigONoz4owSK3PivuZugvKpzzHDKW32gqAb1vuYfQ"]

    print(f'\nResults over {iterations} iterations:')

    for message in msgs:
        unenc_times = []
        enc_times = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            unenc = "RAW: " + message
            unenc.encode("utf-8")
            end = time.perf_counter_ns()

            unenc_times.append( (end - start) / 1000000)

            start = time.perf_counter_ns()
            enc = "ENC: " + encrypt_message(message)
            enc.encode("utf-8")
            end = time.perf_counter_ns()

            enc_times.append( (end - start) / 1000000)
    
        unenc_avg = statistics.mean(unenc_times)
        enc_avg = statistics.mean(enc_times)

        if message.startswith("A"):
            print(f'\nString: "A" * {len(message)}')
        else:
            print(f'\nString: 128 random characters')

        print(f'Without encryption: {unenc_avg:.6f} ms')
        print(f'With encryption: {enc_avg:.6f} ms')
        print(f'Additional time: {enc_avg - unenc_avg:.6f} ms')


def benchmark_rtt(iterations=1000):

    msgs = [
            # strings of diff lengths
                "A", "A" * 16, "A" * 1024, "A" * 4096, "A" * 128, 
            # 128 random characters
            "qu4xpIZWvgRsWNrizWkNcbL3zATmMcVFv7j7mynMXY8GibK704hOiuCerONOX7ROEEt7GabV0S0Kwdo5XMrZ2WutigONoz4owSK3PivuZugvKpzzHDKW32gqAb1vuYfQ"]

    # socket for benchmarking
    bench_socket = socket(AF_INET, SOCK_STREAM)
    bench_socket.connect( (serverName, serverPort) )
    bench_socket.recv(1024)
    bench_socket.sendall(b"benchmark_client")

    all_results = {}

    try:
        for message in msgs:
            results = {"unenc": [], "enc": []}

            for _ in range(iterations):
                for mode in ["unenc", "enc"]:
                    start = time.perf_counter_ns()
                    if mode == "enc":
                        payload = "ENC: " + encrypt_message(message)
                    else:
                        payload = "RAW: " + message
                    send_msg(bench_socket, payload)

                    resp = recv_msg(bench_socket)
                    end = time.perf_counter_ns()

                    if resp != b"ACK":
                        raise RuntimeError (f"Unexpected response: {resp!r}")
                    elapse_ms = (end - start) / 1000000
                    results[mode].append(elapse_ms)
            
            unenc_avg = statistics.mean(results["unenc"])
            enc_avg = statistics.mean(results["enc"])

            unenc_median = statistics.median(results["unenc"])
            enc_median = statistics.median(results["enc"])

            overhead = enc_avg - unenc_avg

            all_results[len(message)] = {
                "unenc_avg": unenc_avg,
                "enc_avg": enc_avg,
                "unenc_median": unenc_median,
                "enc_median": enc_median,
                "overhead": overhead
            }

            print(f"\nMessage size: {len(message)} bytes")
            print(f"Iterations per mode: {iterations}")
            print(f"Unencrypted average RTT: {unenc_avg:.6f} ms")
            print(f"Encrypted average RTT:   {enc_avg:.6f} ms")
            print(f"Unencrypted median RTT:  {unenc_median:.6f} ms")
            print(f"Encrypted median RTT:    {enc_median:.6f} ms")
            print(f"Encryption overhead:     {overhead:.6f} ms")

    finally:
        bench_socket.close()

def receive_messages(clientSocket: socket):
    while True:
        try:
            data = recv_msg(clientSocket)
            if data is None:
                print("Server has shut down")
                break
            print("\nReceived: " + data.decode())
        except OSError:
            print("Lost connection.")
            break

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
    while True:
        try:
            message = input(
                "Enter message to send (or 'exit' to quit):\n"
            )
            if message == "exit":
                break

            if message == "benchmark":
                benchmark()
                continue
            if message == "benchmark_rtt":
                benchmark_rtt()
                continue

            encrypt_choice = input("Encrypt message? (y/n): ")
            if encrypt_choice.lower() == 'y':
                encrypted_text = encrypt_message(message)
                to_send = "ENC:" + encrypted_text
                print(f"Encrypted message to send: {encrypted_text}")
            else:
                to_send = "RAW:" + message

            send_msg(clientSocket, to_send)

        except OSError:
            print("Connection lost")
            break
    clientSocket.close()

if __name__ == "__main__":
    main()
