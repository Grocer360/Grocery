import customtkinter as ctk
import psycopg2
from tkinter import *
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk

# Database connection details
conn_details = {
    "dbname": "grocer360",
    "user": "abdullah",
    "password": "0000",
    "host": "localhost",
    "port": "5432"
}

# Initialize the main application window
root = ctk.CTk()
root.title("Grocer360 Authentication")
root.geometry("900x700")
root.resizable(False, False)  # Disable window resizing
#root.overrideredirect(True) 
root.iconbitmap("myIcon.ico")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

bg = PhotoImage(file = "background.png")
   
canvas1 = Canvas(root)
canvas1.pack(fill = "both", expand = True)
 
canvas1.create_image( 0, 0, image = bg, 
                     anchor = "nw")

# Function to verify login credentials and update logged_in status
def verify_login(username, password, role):
    try:
        conn = psycopg2.connect(**conn_details)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM signers WHERE user_name = %s AND password = %s AND role = %s", (username, password, role))
        user = cursor.fetchone()
        if user:
            cursor.execute("UPDATE signers SET logged_in = %s WHERE user_name = %s", (True, username))
            conn.commit()
        cursor.close()
        conn.close()
        return user is not None
    except Exception as e:
        print(f"Error: {e}")
        return False

# Function to update logged_in status to false
def log_out(username):
    try:
        conn = psycopg2.connect(**conn_details)
        cursor = conn.cursor()
        cursor.execute("UPDATE signers SET logged_in = %s WHERE user_name = %s", (False, username))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Logged Out", "You have successfully logged out.")
        initialize_login_ui(root)
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", "Failed to log out. Please try again.")

# Function to handle sign-in
def sign_in():
    username = username_entry.get()
    password = password_entry.get()
    role = role_var.get()

    if verify_login(username, password, role):
        if role == "admin":
            open_admin_dashboard(username)
        else:
            open_user_dashboard(username)
    else:
        messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")

# Functions to open admin and user dashboards
def open_admin_dashboard(username):
    clear_screen()
    ctk.CTkLabel(root, text="Admin Dashboard", font=("Helvetica", 20)).pack(pady=20)
    create_dashboard_buttons([("Log Out", lambda: log_out(username))])

def open_user_dashboard(username):
    clear_screen()
    ctk.CTkLabel(root, text="User Dashboard", font=("Helvetica", 20)).pack(pady=20)
    create_dashboard_buttons([("Log Out", lambda: log_out(username))])

def create_dashboard_buttons(buttons):
    for text, command in buttons:
        ctk.CTkButton(root, text=text, command=command, width=200, height=40, corner_radius=10).pack(pady=10)

# Function to show the login UI
def initialize_login_ui(root):
    global username_entry, password_entry, role_var

    clear_screen()

    load_BGImg(root, 'background.png', 'background.png')
    load_logoImg(root, "logo.png", "logo.png")

    ctk.CTkLabel(root, text="User Name", font=("Helvetica", 16)).pack(pady=10)
    username_entry = ctk.CTkEntry(root, placeholder_text="Enter your ID", width=250)
    username_entry.pack(pady=10)

    ctk.CTkLabel(root, text="Password", font=("Helvetica", 16)).pack(pady=10)
    password_entry = ctk.CTkEntry(root, show='*', placeholder_text="Enter your password", width=250)
    password_entry.pack(pady=10)

    role_var = StringVar(value="user")
    ctk.CTkLabel(root, text="Role", font=("Helvetica", 16)).pack(pady=10)
    ctk.CTkSegmentedButton(root, variable=role_var, values=["admin", "user"]).pack(pady=5)

    ctk.CTkButton(root, text="Login", command=sign_in, width=200, height=40, corner_radius=10).pack(pady=10)
    ctk.CTkButton(root, text="Face Sign-In", command=show_face_signin, width=200, height=40, corner_radius=10).pack(pady=10)

def load_logoImg(root, light_image_path, dark_image_path):
    try:
        my_image = ctk.CTkImage(light_image=Image.open(light_image_path),
                                dark_image=Image.open(dark_image_path),
                                size=(100, 100))
        image_label = ctk.CTkLabel(root, image=my_image, text="")
        image_label.pack(padx=5, pady=20)
    except IOError as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")


def load_BGImg(root, light_image_path, dark_image_path):
    try:
        my_image = ctk.CTkImage(light_image=Image.open(light_image_path),
                                dark_image=Image.open(dark_image_path),
                                size=(390, 720))
        image_label = ctk.CTkLabel(root, image=my_image, text="")
        image_label.pack(side=LEFT, padx=0)
    except IOError as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")

def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

# Function to show the face sign-in top-level window
def show_face_signin():
    face_signin_window = ctk.CTkToplevel(root)
    face_signin_window.title("Face Sign-In")
    face_signin_window.geometry("400x300")
    face_signin_window.lift()
    face_signin_window.focus_force()
    face_signin_window.grab_set()

    ctk.CTkLabel(face_signin_window, text="Face Sign-In", font=("Helvetica", 20)).pack(pady=20)
    ctk.CTkButton(face_signin_window, text="Simulate Face Sign-In", command=face_signin_success, width=200, height=40, corner_radius=10).pack(pady=20)

def face_signin_success():
    messagebox.showinfo("Face Sign-In", "Face sign-in successful!")
    open_user_dashboard("user")  # Assuming a user role after face sign-in


# Show the sign-in page initially
initialize_login_ui(root)

# Start the main loop
root.mainloop()