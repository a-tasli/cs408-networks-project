def print_to_box(box : ScrolledText, a : string):
    box.configure(state = "enabled")
    box.insert(a)
    box.configure(state = "disabled")