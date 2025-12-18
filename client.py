from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from helpers import *
import socket
import threading
import random

client_socket = None

def listen_to_server():
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                # The server sends "MSG:" as a prefix for text to display
                if msg.startswith("MSG:"):
                    print_to_box(main_console, msg[4:])
                else:
                    print_to_box(main_console, msg)
            else:
                break
        except:
            print_to_box(main_console, "\n[Disconnected from server]\n")
            break

def connect_button_func():
    global client_socket
    try:
        ip = ip_entry.get()
        port = int(port_entry.get())
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        
        print_to_box(main_console, f"Connected to {ip}:{port}\n")
        
        # State Machine: The first thing we send is our Name (JOIN)
        # Since we don't have a name entry, we generate one
        my_name = f"Player_{random.randint(1000,9999)}"
        client_socket.send(my_name.encode())
        print_to_box(main_console, f"Joined as {my_name}\n")
        
        connect_button.configure(state="disabled")
        disconnect_button.configure(state="normal")
        
        # Start listener thread
        t = threading.Thread(target=listen_to_server, daemon=True)
        t.start()
        
    except Exception as e:
        print_to_box(main_console, f"Connection failed: {e}\n")

def disconnect_button_func():
    global client_socket
    if client_socket:
        client_socket.close()
        client_socket = None
    
    connect_button.configure(state="normal")
    disconnect_button.configure(state="disabled")
    print_to_box(main_console, "Disconnected.\n")

def submit_button_func():
    if client_socket:
        choice = choice_selected.get()
        if choice:
            # State Machine: If game is running, sending 'A', 'B', 'C' acts as answering
            client_socket.send(choice.encode())
            print_to_box(main_console, f"Submitted: {choice}\n")

root = Tk()

frame = ttk.Frame(root, padding=10)
frame.grid(sticky="NSEW")

# configure root
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# configure main frame
frame.rowconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)
frame.rowconfigure(2, weight=1)
frame.rowconfigure(3, weight=1)
frame.rowconfigure(4, weight=1)
frame.rowconfigure(5, weight=1)
frame.rowconfigure(6, weight=2)

frame.columnconfigure(0, weight=2)
frame.columnconfigure(1, weight=1)
frame.columnconfigure(2, weight=1)

# the console/monitor that stuff is printed to
main_console = scrolledtext.ScrolledText(frame)
main_console.grid(column=0, row=0, rowspan=8, sticky="NSEW")
main_console.configure(state="disabled")

# labels (text)
ip_label = ttk.Label(frame, text="IP Address:", anchor=W)
ip_label.grid(column=1, row=0, sticky="EW", padx=(6, 6))

port_label = ttk.Label(frame, text="Port:", anchor=W)
port_label.grid(column=1, row=2, sticky="W", padx=(6, 0))

answer_label = ttk.Label(frame, text="Answer:", anchor=W)
answer_label.grid(column=1, row=5, sticky="W", padx=(6, 0))

# entry boxes
ip_entry = ttk.Entry(frame)
ip_entry.insert(0, "127.0.0.1") # Default localhost
ip_entry.grid(column=1, row=1, columnspan=2, sticky="NEW", padx=(6, 0))

port_entry = ttk.Entry(frame)
port_entry.grid(column=1, row=3, columnspan = 2, sticky="NEW", padx=(6, 0))

# child frame to put the radio buttons into
radio_frame = ttk.Frame(frame) 
radio_frame.grid(column=1, row=6, columnspan=2, sticky="NEW", padx=(6, 0)) 

# configure child frame
radio_frame.columnconfigure(0, weight=1)
radio_frame.columnconfigure(1, weight=1)
radio_frame.columnconfigure(2, weight=1)

# radio buttons for choices

choice_selected = StringVar()

a_button = ttk.Radiobutton(radio_frame, text="A", value='A', variable=choice_selected)
a_button.grid(column=0, row=0, sticky="NEW", pady=(6, 0))

b_button = ttk.Radiobutton(radio_frame, text="B", value='B', variable=choice_selected)
b_button.grid(column=1, row=0, sticky="NEW", pady=(6, 0))

c_button = ttk.Radiobutton(radio_frame, text="C", value='C', variable=choice_selected)
c_button.grid(column=2, row=0, sticky="NEW", pady=(6, 0))

# connect button
connect_button = ttk.Button(frame, text="Connect", command=connect_button_func)
connect_button.grid(column=1, row=4, sticky="NEW", padx=(6, 0))

# disconnect button
disconnect_button = ttk.Button(frame, text="Disconnect", command=disconnect_button_func)
disconnect_button.grid(column=2, row=4, sticky="NEW", padx=(0, 0))
disconnect_button.configure(state="disabled")

# submit button
submit_button = ttk.Button(frame, text="Submit", command=submit_button_func)
submit_button.grid(column=1, row=7, columnspan=2, sticky="NSEW", padx=(6, 0), pady=(6, 0))

#start it up
root.mainloop()