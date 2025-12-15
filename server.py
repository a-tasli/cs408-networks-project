from tkinter import *
from tkinter import ttk
root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid(sticky="NSEW")

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

frm.rowconfigure(0, weight=1)
frm.rowconfigure(1, weight=1)
frm.rowconfigure(2, weight=1)
frm.rowconfigure(3, weight=1)
frm.rowconfigure(4, weight=1)
frm.rowconfigure(5, weight=1)
frm.rowconfigure(6, weight=2)
frm.columnconfigure(0, weight=8)
frm.columnconfigure(1, weight=4)
frm.columnconfigure(2, weight=1)

main_console = Listbox(frm).grid(column=0, row=0, rowspan=7, sticky="NSEW")

port_label = ttk.Label(frm, text="Port", anchor=W).grid(column=1, row=0, sticky="EW", padx=(6, 6))
q_amount_label = ttk.Label(frm, text="# of questions", anchor=W).grid(column=1, row=2, sticky="W", padx=(6, 0))
path_label = ttk.Label(frm, text="Path of questions file", anchor=W).grid(column=1, row=4, sticky="W", padx=(6, 0))

port_entry = ttk.Entry(frm).grid(column=1, row=1, sticky="NEW", padx=(6, 0))
q_amount_entry = ttk.Entry(frm).grid(column=1, row=3, columnspan=2, sticky="NEW", padx=(6, 0))
path_entry = ttk.Entry(frm).grid(column=1, row=5, columnspan=2, sticky="NEW", padx=(6, 0))

port_button = ttk.Button(frm, text="Host").grid(column=2, row=1, sticky="NEW", pady=(3, 0))

start_button = ttk.Button(frm, text="Start Game", command=root.destroy).grid(column=1, row=6, columnspan=2, sticky="NSEW", padx=(6, 0), pady=(6, 0))
root.mainloop()
# port number entry
# no of qs
# question filename
# start button
# list box