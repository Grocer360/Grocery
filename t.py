import tkinter as tk
from tkinter import messagebox
import psycopg2
from PIL import Image, ImageTk
import customtkinter as ctk  # Assuming this is your custom tkinter module

# Database connection details (ElephantSQL)
conn_details = {
    "dbname": "okzegkwz", 
    "user": "okzegkwz",
    "password": "7UwFflnPy3byudSr32K1ugHniRSVK6v_",
    "host": "kandula.db.elephantsql.com",
    "port": "5432"
}

# Initialize the main application window
root = ctk.CTk()
root.title("Grocer360 Authentication")
root.geometry("900x700+200+0")
root.resizable(False, False)  # Disable window resizing
root.iconbitmap("myIcon.ico")

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Load background image
bg = tk.PhotoImage(file="background.png")
canvas1 = tk.Canvas(root)
canvas1.pack(fill="both", expand=True)
canvas1.create_image(0, 0, image=bg, anchor="nw")

# Function to verify login credentials and update logged_in status
def verify_login(username, password, role):
    try:
        conn = psycopg2.connect(**conn_details)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE user_name = %s AND password = %s AND role = %s", (username, password, role))
        user = cursor.fetchone()
        if user:
            cursor.execute("UPDATE Users SET logged_in = %s WHERE user_name = %s", (True, username))
            conn.commit()
        cursor.close()
        conn.close()
        return user is not None
    except Exception as e:
        print(f"Error: {e}")
        return False
    
# Function to handle sign-in
def sign_in():
    username = username_entry.get()
    password = password_entry.get()
    role = role_var.get()

    if verify_login(username, password, role):
        messagebox.showinfo("Login Successful", "Login successful!")
    else:
        messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")

# Function to show the login UI
def initialize_login_ui(root):
    global username_entry, password_entry, role_var

    clear_screen()

    load_BGImg(root, 'background.png', 'background.png')
    load_logoImg(root, "logo.png", "logo.png")

    ctk.CTkLabel(root, text="Username", font=("Helvetica", 16)).pack(pady=10)
    username_entry = ctk.CTkEntry(root, placeholder_text="Enter your ID", width=250)
    username_entry.pack(pady=10)

    ctk.CTkLabel(root, text="Password", font=("Helvetica", 16)).pack(pady=10)
    password_entry = ctk.CTkEntry(root, show='*', placeholder_text="Enter your password", width=250)
    password_entry.pack(pady=10)

    role_var = tk.StringVar(value="user")
    ctk.CTkLabel(root, text="Role", font=("Helvetica", 16)).pack(pady=10)
    ctk.CTkSegmentedButton(root, variable=role_var, values=["admin", "user"]).pack(pady=5)

    ctk.CTkButton(root, text="Login", command=sign_in, width=200, height=40, corner_radius=10).pack(pady=10)

    # Load and resize the icon for face sign-in button
    icon_image = Image.open("photo-camera-interface-symbol-for-button.png")
    icon_image = icon_image.resize((25, 25), Image.Resampling.LANCZOS)  # Resize the icon
    icon_photo = ImageTk.PhotoImage(icon_image)

    # Define the face sign-in button with the resized icon
    face_signin_button = ctk.CTkButton(
        #  root,
        # image=icon_photo,
        # text="",  # No text, just the icon
        # command=show_face_signin,  # Use the login function for face sign-in
        # width=10,  # Adjust width as needed
        # height=10,  # Adjust height as needed
        # bg_color="",  # Transparent background
        root,
        image=icon_photo,
        text="use cam to sign in",  # No text, just the icon
        command=show_face_signin,  # Use the login function for face sign-in
        width=10,  # Adjust width as needed
        height=10,  # Adjust height as needed
        fg_color="#242424",  # Make the button transparent
        hover_color=""  # Optional: Change color on hover
    )
    face_signin_button.image = icon_photo  # Keep a reference to the image to prevent garbage collection
    face_signin_button.pack(pady=2)  # Adjust placement as needed

def load_logoImg(root, light_image_path, dark_image_path):
    try:
        my_image = ctk.CTkImage(light_image=Image.open(light_image_path),
                                dark_image=Image.open(dark_image_path),
                                size=(200, 200))
        image_label = ctk.CTkLabel(root, image=my_image, text="")
        image_label.pack(padx=5, pady=20)
    except IOError as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")

def load_BGImg(root, light_image_path, dark_image_path):
    try:
        my_image = ctk.CTkImage(light_image=Image.open(light_image_path),
                                dark_image=Image.open(dark_image_path),
                                size=(400, 720))
        image_label = ctk.CTkLabel(root, image=my_image, text="")
        image_label.pack(side=tk.LEFT, padx=0)
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

# Show the sign-in page initially
initialize_login_ui(root)

# Start the main loop
root.mainloop()
