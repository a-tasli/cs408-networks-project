from tkinter import *
from tkinter import ttk
root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()

main_console = Listbox(frm).grid(column=0, row=0, rowspan=7)

port_label = ttk.Label(frm, text="Port").grid(column=1, row=0)
q_amount_label = ttk.Label(frm, text="# of questions").grid(column=1, row=2)
path_label = ttk.Label(frm, text="Path of questions file").grid(column=1, row=4)

port_entry = ttk.Entry(frm).grid(column=1, row=1)
q_amount_entry = ttk.Entry(frm).grid(column=1, row=3, columnspan=2)
path_entry = ttk.Entry(frm).grid(column=1, row=5, columnspan=2)

port_button = ttk.Button(frm, text="Host").grid(column=2, row=1)

start_button = ttk.Button(frm, text="Start Game", command=root.destroy).grid(column=1, row=7, columnspan=2)
root.mainloop()
# port number entry
# no of qs
# question filename
# start button
# list box