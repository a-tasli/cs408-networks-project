from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import socket
import string

def print_to_box(box : scrolledtext.ScrolledText, a : string):
    box.configure(state = "normal")
    box.insert("end", a)
    box.configure(state = "disabled")


def receive_messages(client_socket, message_callback, disconnect_callback):
    while True:
        try:
            # Block and wait for data
            msg = client_socket.recv(1024).decode()
            
            if msg:
                # If we got a message, run the helper function to show it
                message_callback(msg)
            else:
                # If msg is empty, the server closed the connection gracefully
                disconnect_callback()
                break
                
        except (socket.error, OSError):
            # If an error occurs (crash/timeout), disconnect
            disconnect_callback()
            break
