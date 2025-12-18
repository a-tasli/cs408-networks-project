from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from helpers import *
import socket
import threading

client_socket = None

def listen_to_server():
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                print_to_box(main_console, msg)
            else:
                # Empty message means server closed connection
                break
        except:
            break
    
    # When loop breaks (server disconnected or we quit), update UI
    # Note: modifying UI from thread is risky in Tkinter, but usually works for simple config
    print_to_box(main_console, "\n[Disconnected]\n")
    reset_ui_state()

def reset_ui_state():
    # Helper to reset buttons when disconnected
    connect_button.configure(state="normal")
    disconnect_button.configure(state="disabled")
    # We don't close the socket here because it might already be closed

def connect_button_func():
    global client_socket
    try:
        ip = ip_entry.get()
        port = int(port_entry.get())
        name = name_entry.get()

        if not name:
            print_to_box(main_console, "Please enter a name.\n")
            return
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        
        print_to_box(main_console, f"Connected to {ip}:{port}\n")
        
        # State Machine: The first thing we send is our Name (JOIN)
        client_socket.send(name.encode())
        print_to_box(main_console, f"Joining as {name}...\n")
        
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
        try:
            # Shutdown ensures the server gets the disconnect signal immediately
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
        except:
            pass
        client_socket = None
    
    # UI reset will happen in listen_to_server when the socket breaks, 
    # but we force it here too just in case
    reset_ui_state()

def submit_button_func():
    if client_socket:
        choice = choice_selected.get()
        if choice:
            # State Machine: If game is running, sending 'A', 'B', 'C' acts as answering
            try:
                client_socket.send(choice.encode())
                print_to_box(main_console, f"Submitted: {choice}\n")
            except:
                print_to_box(main_console, "Error sending answer.\n")

root = Tk()
root.title("Quiz Client")

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
frame.rowconfigure(4, weight=1) # Name label
frame.rowconfigure(5, weight=1) # Name entry
frame.rowconfigure(6, weight=1) # Buttons
frame.rowconfigure(7, weight=1) # Answer label
frame.rowconfigure(8, weight=1) # Radio buttons
frame.rowconfigure(9, weight=2) # Submit button

frame.columnconfigure(0, weight=2)
frame.columnconfigure(1, weight=1)
frame.columnconfigure(2, weight=1)

# the console/monitor that stuff is printed to
main_console = scrolledtext.ScrolledText(frame)
main_console.grid(column=0, row=0, rowspan=10, sticky="NSEW")
main_console.configure(state="disabled")

# labels (text)
ip_label = ttk.Label(frame, text="IP Address:", anchor=W)
ip_label.grid(column=1, row=0, sticky="EW", padx=(6, 6))

port_label = ttk.Label(frame, text="Port:", anchor=W)
port_label.grid(column=1, row=2, sticky="W", padx=(6, 0))

name_label = ttk.Label(frame, text="Player Name:", anchor=W)
name_label.grid(column=1, row=4, sticky="W", padx=(6, 0))

answer_label = ttk.Label(frame, text="Answer:", anchor=W)
answer_label.grid(column=1, row=7, sticky="W", padx=(6, 0))

# entry boxes
ip_entry = ttk.Entry(frame)
ip_entry.insert(0, "127.0.0.1")
ip_entry.grid(column=1, row=1, columnspan=2, sticky="NEW", padx=(6, 0))

port_entry = ttk.Entry(frame)
port_entry.grid(column=1, row=3, columnspan = 2, sticky="NEW", padx=(6, 0))

name_entry = ttk.Entry(frame)
name_entry.grid(column=1, row=5, columnspan=2, sticky="NEW", padx=(6, 0))

# connect button
connect_button = ttk.Button(frame, text="Connect", command=connect_button_func)
connect_button.grid(column=1, row=6, sticky="NEW", padx=(6, 0))

# disconnect button
disconnect_button = ttk.Button(frame, text="Disconnect", command=disconnect_button_func)
disconnect_button.grid(column=2, row=6, sticky="NEW", padx=(0, 0))
disconnect_button.configure(state="disabled")

# child frame to put the radio buttons into
radio_frame = ttk.Frame(frame) 
radio_frame.grid(column=1, row=8, columnspan=2, sticky="NEW", padx=(6, 0)) 

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

# submit button
submit_button = ttk.Button(frame, text="Submit", command=submit_button_func)
submit_button.grid(column=1, row=9, columnspan=2, sticky="NSEW", padx=(6, 0), pady=(6, 0))

#start it up
root.mainloop()