from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from helpers import *
from game_logic import *

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
    print_to_box(main_console, current_quiz.scoreboard_printable())

    start_button.configure(state = "disabled")

def host_button_func():
    # TODO check if ip and port are correct
    # TODO host server, check errors
    # TODO listen port for connections
    host_button.configure(state = "disabled")
    

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