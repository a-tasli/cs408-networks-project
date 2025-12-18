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
            pass

def send_private_feedback():
    """Sends individual feedback to each player about their answer status."""
    for sock, name in clients.items():
        status = current_quiz.player_status.get(name)
        msg = ""
        if status == 'F':
            msg = "\nCorrect! You answered first (+ Bonus Points)!\n"
        elif status == 'C':
            msg = "\nCorrect!\n"
        elif status == 'W':
            msg = "\nWrong answer.\n"
        
        if msg:
            try:
                sock.send(msg.encode())
            except:
                pass

def handle_client(conn, addr):
    global current_quiz
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
                player_name = msg.strip()
                if current_quiz.add_player(player_name) == 0:
                    clients[conn] = player_name
                    print_to_box(main_console, f"{player_name} has joined.\n")
                    broadcast(f"{player_name} joined the lobby.\n")
                else:
                    # Name taken or invalid
                    conn.send("Name unavailable. Please reconnect with a different name.\n".encode())
                    # Close connection to force client reset
                    conn.close()
                    return # Exit thread
            
            # State 2: Game Started -> Msg is Answer (A/B/C)
            else:
                if player_name:
                    res = current_quiz.give_answer(player_name, msg)
                    if res == 0:
                        print_to_box(main_console, f"{player_name} answered {msg}.\n")
                        conn.send("Answer received.\n".encode())
                        
                        # Check State Transition
                        if current_quiz.check_if_all_answered():
                            # 1. Send Feedback to individual players
                            send_private_feedback()
                            
                            # 2. Update Scores
                            current_quiz.update_scores()
                            
                            # 3. Broadcast Scoreboard
                            sb = current_quiz.scoreboard_printable()
                            broadcast(f"\n--- ROUND OVER ---\n{sb}\n")
                            # Print scoreboard to server console as well
                            print_to_box(main_console, f"\n--- ROUND OVER ---\n{sb}\n")
                            
                            # Next Question or End Game
                            if current_quiz.next_question() == 0:
                                q_text = current_quiz.current_question_printable()
                                broadcast(f"\n{q_text}\n")
                                print_to_box(main_console, f"\n{q_text}\n")
                            else:
                                # Prepare final scoreboard
                                final_sb = current_quiz.scoreboard_printable()
                                broadcast(f"\n--- GAME OVER ---\nFINAL SCORES:\n{final_sb}\n")
                                print_to_box(main_console, f"\n--- GAME OVER ---\nFINAL SCORES:\n{final_sb}\n")
                                print_to_box(main_console, "Game Over. Resetting.\n")
                                
                                # Disconnect all players
                                for sock in list(clients.keys()):
                                    try:
                                        sock.shutdown(socket.SHUT_RDWR)
                                    except:
                                        pass
                                    try:
                                        sock.close()
                                    except:
                                        pass
                                
                                # Log disconnect for this thread (since we return early)
                                print_to_box(main_console, f"{player_name} disconnected.\n")

                                # Full Reset: Create new Quiz object
                                current_quiz = Quiz() 
                                clients.clear()
                                start_button.configure(state="normal")
                                return
                    else:
                        conn.send("You already answered this round.\n".encode())
                else:
                    # Late joiner attempting to connect after game start
                    conn.send("Game already in progress. Connection refused.\n".encode())
                    break

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break

    # Cleanup (Player Disconnect)
    if player_name:
        current_quiz.drop_player(player_name)
        broadcast(f"{player_name} left the game.\n")
        print_to_box(main_console, f"{player_name} disconnected.\n")
    
    if conn in clients:
        del clients[conn]
    
    try:
        conn.close()
    except:
        pass
        
    # Check if game should end due to lack of players
    # We use global current_quiz here because it might have been replaced in another thread
    if current_quiz.started and len(current_quiz.players) < 2:
        print_to_box(main_console, "Not enough players. Game Over.\n")
        
        # Prepare final scoreboard
        final_sb = current_quiz.scoreboard_printable()
        broadcast(f"\nNot enough players remaining. Game ended.\nFINAL SCORES:\n{final_sb}\n")
        print_to_box(main_console, f"\nNot enough players remaining. Game ended.\nFINAL SCORES:\n{final_sb}\n")
        
        # Disconnect any remaining players (the 1 survivor)
        for sock in list(clients.keys()):
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                sock.close()
            except:
                pass
        
        # Log disconnect for this thread if strictly needed (usually covered by cleanup if we didn't return)
        # However, we are resetting current_quiz below, so standard cleanup might fail logic on 'drop_player'
        # safely logging here ensures visibility
        if player_name:
             print_to_box(main_console, f"{player_name} disconnected.\n")

        # Full Reset: Create new Quiz object
        current_quiz = Quiz()
        clients.clear()
        start_button.configure(state="normal")

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
    broadcast("\n--- GAME STARTED ---\n")
    q_text = current_quiz.current_question_printable()
    broadcast(f"{q_text}\n")
    print_to_box(main_console, f"{q_text}\n")

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
root.title("Quiz Server")
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