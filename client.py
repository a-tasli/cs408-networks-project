from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext

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

# labels (text)
ip_label = ttk.Label(frame, text="IP Address:", anchor=W)
ip_label.grid(column=1, row=0, sticky="EW", padx=(6, 6))

port_label = ttk.Label(frame, text="Port:", anchor=W)
port_label.grid(column=1, row=2, sticky="W", padx=(6, 0))

answer_label = ttk.Label(frame, text="Answer:", anchor=W)
answer_label.grid(column=1, row=5, sticky="W", padx=(6, 0))

# entry boxes
ip_entry = ttk.Entry(frame)
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
connect_button = ttk.Button(frame, text="Connect")
connect_button.grid(column=1, row=4, sticky="NEW", padx=(6, 0))

# disconnect button
disconnect_button = ttk.Button(frame, text="Disconnect")
disconnect_button.grid(column=2, row=4, sticky="NEW", padx=(0, 0))

def debug():
    print(choice_selected.get())

# submit button
submit_button = ttk.Button(frame, text="Submit", command=debug)
submit_button.grid(column=1, row=7, columnspan=2, sticky="NSEW", padx=(6, 0), pady=(6, 0))

#start it up
root.mainloop()