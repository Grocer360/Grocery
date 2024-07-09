import tkinter as tk
import customtkinter as ctk
from register import RegisterUserApp  # Assuming RegisterUserApp is defined in a separate file
from manage import ManageUsersApp  # Assuming ManageUsersApp is defined in a separate file

def sign_up():
    print("Sign Up clicked")

def sign_up_with_face():
    print("Sign Up with Face clicked")
    register_window = ctk.CTk()  # Create a new top-level window using ctk.CTk
    app = RegisterUserApp(register_window)  # Create an instance of RegisterUserApp
    register_window.mainloop()  # Start the main loop for the registration window

def manage_button():
    print("Manage clicked")
    manage_window = ctk.CTk()  # Create a new top-level window using ctk.CTk
    app = ManageUsersApp(manage_window)  # Create an instance of ManageUsersApp
    manage_window.mainloop()  # Start the main loop for the management window

# Create the main window
root = ctk.CTk()
root.title("Sign In")

# Create a frame for better organization (optional)
frame = ctk.CTkFrame(root)
frame.pack(padx=50, pady=50)

# Create a Sign Up button
btn_sign_up = ctk.CTkButton(frame, text="Sign Up", width=20, command=sign_up)
btn_sign_up.pack(pady=10)

# Create a Sign Up with Face button
btn_sign_up_face = ctk.CTkButton(frame, text="Sign Up with Face", width=20, command=sign_up_with_face)
btn_sign_up_face.pack(pady=10)

# Create a Manage button
btn_manage = ctk.CTkButton(frame, text="Manage", width=20, command=manage_button)
btn_manage.pack(pady=10)

# Start the main loop
root.mainloop()
