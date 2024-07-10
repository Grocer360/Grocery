import tkinter as tk
import customtkinter as ctk
from register import RegisterUserApp  # Assuming RegisterUserApp is defined in a separate file
from manage import ManageUsersApp  # Assuming ManageUsersApp is defined in a separate file
from login import FaceRecognitionApp  # Assuming FaceRecognitionApp is defined in a separate file

def log_in():
    try:
        print("Log in clicked")
        login_window = ctk.CTk()  # Create a new top-level window using ctk.CTk
        app = FaceRecognitionApp(login_window)  # Create an instance of FaceRecognitionApp
        login_window.mainloop()  # Start the main loop for the login window
    except Exception as e:
        print(f"Error during log in: {e}")

def sign_up_with_face():
    try:
        print("Sign Up with Face clicked")
        register_window = ctk.CTk()  # Create a new top-level window using ctk
        app = RegisterUserApp(register_window)  # Create an instance of RegisterUserApp
        register_window.mainloop()  # Start the main loop for the registration window
    except Exception as e:
        print(f"Error during sign up with face: {e}")

def manage_button():
    try:
        print("Manage clicked")
        manage_window = ctk.CTk()  # Create a new top-level window using ctk
        app = ManageUsersApp(manage_window)  # Create an instance of ManageUsersApp
        manage_window.mainloop()  # Start the main loop for the management window
    except Exception as e:
        print(f"Error during manage: {e}")

# Create the main window
try:
    root = ctk.CTk()
    root.title("Sign In")

    # Create a frame for better organization (optional)
    frame = ctk.CTkFrame(root)
    frame.grid(padx=50, pady=50)

    # Create a Sign Up button
    btn_sign_up = ctk.CTkButton(frame, text="Log In", width=20, command=log_in)
    btn_sign_up.grid(row=0, column=0, pady=10)

    # Create a Sign Up with Face button
    btn_sign_up_face = ctk.CTkButton(frame, text="Sign Up with Face", width=20, command=sign_up_with_face)
    btn_sign_up_face.grid(row=1, column=0, pady=10)

    # Create a Manage button
    btn_manage = ctk.CTkButton(frame, text="Manage", width=20, command=manage_button)
    btn_manage.grid(row=2, column=0, pady=10)

    # Start the main loop
    root.mainloop()
except Exception as e:
    print(f"Error in main application: {e}")
