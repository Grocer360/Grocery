import tkinter as tk
from tkinter import messagebox
from login import FaceRecognitionApp  # Make sure to import the updated FaceRecognitionApp

# Function to validate the login with username and password
def loginAction():
    # Sample hardcoded username and password
    username = "admin"
    password = "password123"

    # Get the input from the entry fields
    entered_username = entry_username.get()
    entered_password = entry_password.get()

    # Check if the entered credentials match the hardcoded ones
    if entered_username == username and entered_password == password:
        messagebox.showinfo("Login Successful", "Welcome!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# Function to open the face recognition login window
def openFaceLogin():
    face_recognition_app = FaceRecognitionApp(root)
    face_recognition_app.mainloop()

# Create the main application window
root = tk.Tk()
root.title("Login Page")

# Set the size of the window
root.geometry("300x600")

# Add a label for the username
label_username = tk.Label(root, text="Username:")
label_username.pack(pady=10)

# Add an entry field for the username
entry_username = tk.Entry(root)
entry_username.pack(pady=5)

# Add a label for the password
label_password = tk.Label(root, text="Password:")
label_password.pack(pady=10)

# Add an entry field for the password (with hidden input)
entry_password = tk.Entry(root, show="*")
entry_password.pack(pady=5)

# Add a login button and associate it with the login function
login_button = tk.Button(root, text="Login", command=loginAction)
login_button.pack(pady=20)

# Add a button for "Login with Face" and associate it with the face recognition function
login_with_face_button = tk.Button(root, text="Login with Face", command=openFaceLogin)
login_with_face_button.pack(pady=20)

# Add a quit button to close the application
quit_button = tk.Button(root, text="Quit", command=root.quit)
quit_button.pack()

# Run the application
root.mainloop()
