import socket
import threading

def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")
    # TODO probably keep a list of clients here
    while True:
        try:
            # Receive message from this specific client
            message = client_socket.recv(1024).decode()
            if not message:
                # graceful close
                break
            print(f"[{address}] {message}")
        except:
            # error close
            break
    
    client_socket.close()
    print(f"[DISCONNECTED] {address} closed.")

# TODO make this function
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 12345))
server.listen()

print("[LISTENING] Server is looking for connections...")

# TODO do this with thread
while True:
    # Accept new connections in a loop
    conn, addr = server.accept()
    # Create a new thread for every new client
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()