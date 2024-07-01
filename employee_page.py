
from tkinter import ttk



def create_user_page(container):
    user_frame = ttk.Frame(container)
    user_frame.grid(row=0, column=0, sticky='nsew')

    ttk.Label(user_frame, text="Welcome to the User Page").pack(padx=20, pady=20)

    return user_frame
