import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            # Constantly watch for incoming data
            message = client_socket.recv(1024).decode()
            if message:
                print(f"\n[SERVER]: {message}")
            else:
                break
        except:
            print("[ERROR] Connection lost.")
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

# Start a background thread to listen for server messages
receive_thread = threading.Thread(target=receive_messages, args=(client,))
receive_thread.daemon = True # Ends the thread when the main program stops
receive_thread.start()

# Main thread handles sending messages
print("Type messages below (or 'quit' to exit):")
while True:
    msg = input("> ")
    if msg.lower() == 'quit':
        break
    client.send(msg.encode())

client.close()