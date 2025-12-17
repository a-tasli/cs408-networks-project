import socket
import threading

def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")
    while True:
        try:
            # Receive message from this specific client
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"[{address}] {message}")
        except:
            break
    
    client_socket.close()
    print(f"[DISCONNECTED] {address} closed.")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 12345))
server.listen()

print("[LISTENING] Server is looking for connections...")

while True:
    # Accept new connections in a loop
    conn, addr = server.accept()
    # Create a new thread for every new client
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()