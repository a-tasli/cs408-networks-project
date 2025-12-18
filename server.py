from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from helpers import *
from game_logic import *
import socket
import threading

# parse quiz files
def parse(file_path):
    questions = [] # each element is a string
    answers = [] # each element is capital letter

    try:
        file = open(file_path, "r")
    except OSError:
        return -1 # couldnt open file

    with file: # file closes automatically
        lines = file.readlines() # get all lines as a list
        for i in range(len(lines))[::5]: # iterate 5 by 5
            questions.append("".join(lines[i:i+4])) # append next 4 lines as question
            answers.append(lines[i+4][-2]) # append last character as answer (A, B, C)

    return questions, answers

current_quiz = Quiz() # make new quiz
clients = {} # socket : player_name
server_socket = None

def broadcast(msg):
    for client in list(clients.keys()):
        try:
            client.send(msg.encode())
        except:
            # If sending fails, assume disconnected
            pass

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    player_name = None

    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            
            # STATE MACHINE LOGIC
            
            # State 1: Lobby (Not Started) -> Msg is Player Name
            if not current_quiz.started:
                player_name = msg
                if current_quiz.add_player(player_name) == 0:
                    clients[conn] = player_name
                    print_to_box(main_console, f"{player_name} has joined.\n")
                    broadcast(f"MSG:{player_name} joined the lobby.\n")
                else:
                    conn.send("MSG:Error: Name taken or invalid.\n".encode())
            
            # State 2: Game Started -> Msg is Answer (A/B/C)
            else:
                if player_name:
                    res = current_quiz.give_answer(player_name, msg)
                    if res == 0:
                        print_to_box(main_console, f"{player_name} answered {msg}.\n")
                        conn.send("MSG:Answer received.\n".encode())
                        
                        # Check State Transition
                        if current_quiz.check_if_all_answered():
                            current_quiz.update_scores()
                            broadcast(f"MSG:\n--- ROUND OVER ---\n{current_quiz.scoreboard_printable()}\n")
                            
                            # Next Question or End Game
                            if current_quiz.next_question() == 0:
                                q_text = current_quiz.current_question_printable()
                                broadcast(f"MSG:\nNEXT QUESTION:\n{q_text}\n")
                            else:
                                broadcast("MSG:\n--- GAME OVER ---\n")
                    else:
                        conn.send("MSG:You already answered this round.\n".encode())

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break

    # Cleanup
    if player_name:
        current_quiz.drop_player(player_name)
        broadcast(f"MSG:{player_name} left the game.\n")
        print_to_box(main_console, f"{player_name} disconnected.\n")
    
    if conn in clients:
        del clients[conn]
    
    conn.close()

def accept_clients():
    while True:
        try:
            conn, addr = server_socket.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
        except:
            break

def start_button_func():
    # check player count
    if len(current_quiz.players) < 2:
        print_to_box(main_console, "Not enough players to start a game.\n")
        return

    # quiz file stuff
    val = parse(path_entry.get())
    if val == -1:
        print_to_box(main_console, "Couldn't open quiz input file.\n")
        return
    if not q_amount_entry.get().isnumeric() or int(q_amount_entry.get()) < 1:
        print_to_box(main_console, "Invalid question amount.\n")
        return

    # start quiz
    current_quiz.set_qa(val[0], val[1])
    current_quiz.start(int(q_amount_entry.get()))
    
    # Broadcast start
    print_to_box(main_console, "Game Started!\n")
    broadcast("MSG:\n--- GAME STARTED ---\n")
    broadcast(f"MSG:{current_quiz.current_question_printable()}\n")

    start_button.configure(state = "disabled")

def host_button_func():
    global server_socket
    try:
        port = int(port_entry.get())
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()
        
        print_to_box(main_console, f"Server hosted on port {port}.\n")
        host_button.configure(state = "disabled")
        
        # Start accepting clients in a thread
        t = threading.Thread(target=accept_clients, daemon=True)
        t.start()
        
    except Exception as e:
        print_to_box(main_console, f"Error hosting server: {e}\n")
    

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
frame.columnconfigure(0, weight=8)
frame.columnconfigure(1, weight=4)
frame.columnconfigure(2, weight=1)

# the console/monitor that stuff is printed to
main_console = scrolledtext.ScrolledText(frame)
main_console.grid(column=0, row=0, rowspan=7, sticky="NSEW")
main_console.configure(state ='disabled')

# labels (text)
port_label = ttk.Label(frame, text="Port", anchor=W)
port_label.grid(column=1, row=0, sticky="EW", padx=(6, 6))

q_amount_label = ttk.Label(frame, text="# of questions", anchor=W)
q_amount_label.grid(column=1, row=2, sticky="W", padx=(6, 0))

path_label = ttk.Label(frame, text="Path to questions file", anchor=W)
path_label.grid(column=1, row=4, sticky="W", padx=(6, 0))

# entry boxes
port_entry = ttk.Entry(frame)
port_entry.grid(column=1, row=1, sticky="NEW", padx=(6, 0))

q_amount_entry = ttk.Entry(frame)
q_amount_entry.grid(column=1, row=3, columnspan=2, sticky="NEW", padx=(6, 0))

path_entry = ttk.Entry(frame)
path_entry.grid(column=1, row=5, columnspan=2, sticky="NEW", padx=(6, 0))

# host button
host_button = ttk.Button(frame, text="Host", command=host_button_func)
host_button.grid(column=2, row=1, sticky="NEW", pady=(3, 0))

# start game button
start_button = ttk.Button(frame, text="Start Game", command=start_button_func)
start_button.grid(column=1, row=6, columnspan=2, sticky="NSEW", padx=(6, 0), pady=(6, 0))

# start it up
root.mainloop()