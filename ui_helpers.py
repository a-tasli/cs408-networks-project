def print_to_box(box : ScrolledText, a : string):
    box.configure(state = "enabled")
    box.insert(a)
    box.configure(state = "disabled")

def start_button_func():
    port_value = port_entry.get()
    q_amount_value = q_amount_entry.get()
    path_value = path_entry.get()

def disable_host_button(host_button):
    host_button.configure(state = "disabled")

def enable_host_button(host_button):
    host_button.configure(state = "enabled")
