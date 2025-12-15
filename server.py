from tkinter import *
from tkinter import ttk
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
main_console = Listbox(frame).grid(column=0, row=0, rowspan=7, sticky="NSEW")

# labels (text)
port_label = ttk.Label(frame, text="Port", anchor=W).grid(column=1, row=0, sticky="EW", padx=(6, 6))
q_amount_label = ttk.Label(frame, text="# of questions", anchor=W).grid(column=1, row=2, sticky="W", padx=(6, 0))
path_label = ttk.Label(frame, text="Path of questions file", anchor=W).grid(column=1, row=4, sticky="W", padx=(6, 0))

# entry boxes
port_entry = ttk.Entry(frame).grid(column=1, row=1, sticky="NEW", padx=(6, 0))
q_amount_entry = ttk.Entry(frame).grid(column=1, row=3, columnspan=2, sticky="NEW", padx=(6, 0))
path_entry = ttk.Entry(frame).grid(column=1, row=5, columnspan=2, sticky="NEW", padx=(6, 0))

# port button
port_button = ttk.Button(frame, text="Host").grid(column=2, row=1, sticky="NEW", pady=(3, 0))

# start game button
start_button = ttk.Button(frame, text="Start Game", command=root.destroy).grid(column=1, row=6, columnspan=2, sticky="NSEW", padx=(6, 0), pady=(6, 0))

# start it up
root.mainloop()