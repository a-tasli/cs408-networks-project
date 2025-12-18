from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import socket
import threading
import string

# helper
def print_to_box(box : scrolledtext.ScrolledText, a : string):
    box.configure(state = "normal")
    box.insert("end", a)
    box.configure(state = "disabled")

client_socket = None

# only job of client is to print whatever server sends, and send name/answer to server
def listen_to_server():
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                print_to_box(main_console, msg)
            else:
                # empty message means server closed connection
                print_to_box(main_console, "\nDisconnected.\n")
                break
        except:
            # abrupt disconnection
            print_to_box(main_console, "\nAbruptly disconnected.\n")
            break
    
    # server disconnected or we quit -> update ui
    reset_ui_state()

def reset_ui_state():
    connect_button.configure(state="normal")
    disconnect_button.configure(state="disabled")
    submit_button.configure(state="disabled")

def connect_button_func():
    global client_socket
    try:
        ip = ip_entry.get()
        port = int(port_entry.get())
        name = name_entry.get()

        if not name:
            print_to_box(main_console, "Please enter a name.\n")
            return
        
        # open socket/connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        print_to_box(main_console, f"Connected to {ip}:{port}\n")
        
        # send our name first
        client_socket.send(name.encode())
        print_to_box(main_console, f"Joining as {name}...\n")
        
        # ui state
        connect_button.configure(state="disabled")
        disconnect_button.configure(state="normal")
        submit_button.configure(state="normal")
        
        # start listener thread (ui shouldnt freeze)
        t = threading.Thread(target=listen_to_server, daemon=True)
        t.start()
        
    except Exception as e:
        print_to_box(main_console, f"Connection failed: {e}\n")

def disconnect_button_func():
    global client_socket
    if client_socket: # if connected
        try:
            # shutdown ensures the server gets the disconnect signal immediately
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
        except:
            print_to_box(main_console, f"Disconnect failed(??)\n") # shouldnt get here
        client_socket = None
    
    # ui reset will happen in listen_to_server anyway
    # but we force it here too just in case
    reset_ui_state()

def submit_button_func():
    if client_socket: # if connected
        choice = choice_selected.get()
        if choice:
            # if game is running sending 'A', 'B', 'C' counts as answering (rather than player name)
            try:
                client_socket.send(choice.encode())
                print_to_box(main_console, f"Submitted: {choice}\n")
            except:
                print_to_box(main_console, "Error sending answer.\n")
        else:
            print_to_box(main_console, "Please select an answer before submitting.\n")


# -- ui creation --

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
frame.rowconfigure(4, weight=1) # name label
frame.rowconfigure(5, weight=1) # name entry
frame.rowconfigure(6, weight=1) # buttons
frame.rowconfigure(7, weight=1) # answer label
frame.rowconfigure(8, weight=1) # radio buttons
frame.rowconfigure(9, weight=2) # submit button

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
submit_button.configure(state="disabled")

# start it up
root.mainloop()