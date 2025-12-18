from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import socket
import threading
import string

# create and manage quizzes
class Quiz:
    def __init__(self):
        self.players = []
        self.questions = []
        self.question_count = 0
        self.answers = [] # answer is capital letter
        self.scoreboard = {} # player : score
        self.question_index = 0
        self.started = False
        self.player_answered = {} # player : true/false
        self.player_status = {} # player : correct/first/wrong
        self.first_taken = False # someone answered first and took all points

    def add_player(self, player_name):
        if self.players.count(player_name) > 0:
            return -1 # player already exists, shouldnt allow connection
        self.players.append(player_name)
        return 0

    def drop_player(self, player_name):
        if self.players.count(player_name) == 0:
            return -1 # player does not exist
        self.players.remove(player_name)
        return 0

    def set_qa(self, questions, answers):
        self.questions = questions
        self.answers = answers

    def start(self, question_count):
        self.question_count = question_count
        self.question_index = 0
        self.started = True
        self.first_taken = False
        for p in self.players:
            self.scoreboard[p] = 0
            self.player_answered[p] = False
            self.player_status[p] = '0'
    
    def next_question(self):
        self.question_index += 1
        if self.question_index >= self.question_count:
            return -1 # game should end

        self.first_taken = False
        for p in self.players:
            self.player_answered[p] = False
            self.player_status[p] = '0'
        return 0
    
    def give_answer(self, player_name, answer): # answer is capital letter
        if self.player_answered[player_name]:
            return -1 # you already answered dummy

        self.player_answered[player_name] = True # they are answering
        if answer == self.answers[self.question_index % len(self.answers)]: # correct answer, can loop
            if not self.first_taken: # bonus points, total equal to player count
                self.first_taken = True
                self.player_status[player_name] = 'F' # first
            else:
                self.player_status[player_name] = 'C' # correct
        else:
            self.player_status[player_name] = 'W' # wrong

        return 0

    def check_if_all_answered(self):
        count = 0
        for p in self.players: # only count players that are in the game
            if self.player_answered[p]:
                count += 1

        return count == len(self.players) # true if all players answered

    def update_scores(self):
        for p in self.players:
            if self.player_status[p] == 'F':
                self.scoreboard[p] += len(self.players) # bonus points
            elif self.player_status[p] == 'C':
                self.scoreboard[p] += 1

    def scoreboard_printable(self):
        board = ""
        sorted_items = sorted(self.scoreboard.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

        rank = 1
        count = 1
        for item in sorted_items:
            board += f"{rank}. {item[0]}, with {item[1]} points\n"
            count += 1
            # only increase if no tie
            if count <= len(sorted_items) and item[1] > sorted_items[count-1][1]:
                rank = count

        return board

    def current_question_printable(self):
        return self.questions[self.question_index % len(self.questions)] # looping questions
        

# helper
def print_to_box(box : scrolledtext.ScrolledText, a : string):
    box.configure(state = "normal")
    box.insert("end", a)
    box.configure(state = "disabled")

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

def send_private_feedback(): # sent to all players but each message is personalised
    for sock, name in clients.items():
        status = current_quiz.player_status.get(name)
        msg = ""
        if status == 'F':
            msg = f"\nCorrect! (+ {len(current_quiz.players) - 1} Bonus Points)\n"
        elif status == 'C':
            msg = "\nCorrect!\n"
        elif status == 'W':
            msg = "\nWrong answer.\n"
        
        if msg: # status could be '0' if player left
            try:
                sock.send(msg.encode())
            except:
                pass

def progress_game():
    global current_quiz
    # send feedback to individual players
    send_private_feedback()
    
    # update scores
    current_quiz.update_scores()
    
    # broadcast scoreboard
    sb = current_quiz.scoreboard_printable()
    broadcast(f"\n--- ROUND OVER ---\n{sb}")
    # print scoreboard to server console as well
    print_to_box(main_console, f"\nScoreboard:\n{sb}")
    
    # next question
    if not current_quiz.next_question():
        q_text = current_quiz.current_question_printable()
        ans_text = current_quiz.answers[current_quiz.question_index]
        broadcast(f"\n{q_text}")
        print_to_box(main_console, f"\n{q_text}")
        print_to_box(main_console, f"Answer: {ans_text}\n")
        return False # game continues
    else: # out of questions
        # prepare final scoreboard
        final_sb = current_quiz.scoreboard_printable()
        broadcast(f"\n--- GAME OVER ---\nFINAL SCORES:\n{final_sb}\n")
        print_to_box(main_console, f"\nGame over.\nFinal scoreboard:\n{final_sb}\n")
        print_to_box(main_console, "Resetting.\n")
        
        # disconnect all players
        for sock in list(clients.keys()): # try closing all of them just in case
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                sock.close()
            except:
                pass

        # create new quiz object / clear clients
        current_quiz = Quiz() 
        clients.clear()
        start_button.configure(state="normal")
        return True # game over

def handle_client(conn, addr):
    global current_quiz
    print_to_box(main_console, f"New connection from: {addr}\n")
    player_name = None

    # game loop / call class functions
    while True:
        try:
            msg = conn.recv(1024).decode() # get message
            if not msg: # client disconnected
                break
            
            # lobby state
            if not current_quiz.started:
                if player_name is None: # if the player hasnt joined yet
                    name_attempt = msg.strip() # msg sent is name
                    if not current_quiz.add_player(name_attempt): # name not taken
                        player_name = name_attempt # take name
                        clients[conn] = player_name
                        print_to_box(main_console, f"{player_name} has joined.\n")
                        broadcast(f"{player_name} joined the lobby.\n")
                    else: # name was already taken (add_player returned -1)
                        conn.send("Name unavailable. Please reconnect with a different name.\n".encode())
                        print_to_box(main_console, f"Name {name_attempt} was taken, disconnecting client.\n")
                        # close connection to force client reset
                        conn.close()
                        return
                else:
                    # impatient client pressed button early right after joining
                    conn.send("Game has not started yet. Please wait.\n".encode())
            
            # quiz state -> msg is answer A, B, C
            else:
                if player_name: # player is in lobby
                    duplicate_ans = current_quiz.give_answer(player_name, msg)
                    if not duplicate_ans:
                        print_to_box(main_console, f"{player_name} answered {msg}.\n")
                        conn.send("Answer received.\n".encode()) # acknowledgement
                        
                        # check state transition
                        if current_quiz.check_if_all_answered():
                            game_over = progress_game()
                            if game_over:
                                # log disconnect for this thread (since we return early)
                                print_to_box(main_console, f"{player_name} disconnected.\n")
                                return
                    else:
                        conn.send("You already answered this round.\n".encode())
                else: # game already in progress, reject client
                    conn.send("Game already in progress. Connection refused.\n".encode())
                    print_to_box(main_console, f"{addr} tried to join while game was in progress, disconnecting client.\n")
                    # close connection to force client reset
                    conn.close()
                    return

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break

    # cleanup
    if player_name:
        current_quiz.drop_player(player_name)
        broadcast(f"{player_name} left the game.\n") # send it to everyone else
        print_to_box(main_console, f"{player_name} disconnected.\n")
    
    if conn in clients:
        del clients[conn]
    
    try:
        conn.close() # one final close attempt just in case
    except:
        pass
        
    # check if game should end due to lack of players
    if current_quiz.started and len(current_quiz.players) < 2:
        # prepare final scoreboard
        final_sb = current_quiz.scoreboard_printable()
        broadcast(f"\nNot enough players remaining. Game over.\nFINAL SCORES:\n{final_sb}\n")
        print_to_box(main_console, f"\nNot enough players remaining. Game ended.\nFinal scoreboard:\n{final_sb}\n")
        
        # disconnect any remaining players
        for sock in list(clients.keys()):
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                sock.close()
            except:
                pass
        
        if player_name and current_quiz.players.count(player_name): # i am the last player and im ending the game
            print_to_box(main_console, f"{player_name} disconnected.\n")

        # reset quiz and client list
        current_quiz = Quiz()
        clients.clear()
        start_button.configure(state="normal")
        return

    # the disconnected player was the last one needed to answer
    if current_quiz.started and current_quiz.check_if_all_answered():
        progress_game()

def accept_clients():
    while True:
        try:
            conn, addr = server_socket.accept()
            # start a thread for each client, concurrency is needed
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
        except:
            break # just in case

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
    
    # broadcast start
    print_to_box(main_console, "Game started.\n")
    broadcast("\n--- GAME STARTED ---\n")
    q_text = current_quiz.current_question_printable()
    broadcast(q_text)
    print_to_box(main_console, q_text)
    print_to_box(main_console, f"Answer: {current_quiz.answers[0]}\n")

    start_button.configure(state = "disabled") # update ui

def host_button_func():
    global server_socket
    try:
        port = int(port_entry.get())
        # open connection
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()
        
        print_to_box(main_console, f"Server hosted on port {port}.\n")
        host_button.configure(state = "disabled")
        
        # start accepting clients in a new thread (ui shouldnt freeze)
        t = threading.Thread(target=accept_clients, daemon=True)
        t.start()
        
    except Exception as e:
        print_to_box(main_console, f"Error hosting server: {e}\n")


# -- ui creation --

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
port_label = ttk.Label(frame, text="Port:", anchor=W)
port_label.grid(column=1, row=0, sticky="EW", padx=(6, 6))

q_amount_label = ttk.Label(frame, text="# of questions:", anchor=W)
q_amount_label.grid(column=1, row=2, sticky="W", padx=(6, 0))

path_label = ttk.Label(frame, text="Path to questions file:", anchor=W)
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