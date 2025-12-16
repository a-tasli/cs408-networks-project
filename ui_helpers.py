from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import string

def print_to_box(box : scrolledtext.ScrolledText, a : string):
    box.configure(state = "normal")
    box.insert("end", a)
    box.configure(state = "disabled")