import customtkinter as ctk
import psycopg2
from tkinter import *
from tkinter import messagebox

from PIL import Image, ImageTk
from admin_dashboard import AdminDashboard
from user_dashboard import UserDashboard
from face_auth import FaceSignIn


# Database connection details
conn_details = {
    "dbname": "grocery_database_system",
    "user": "anas",
    "password": "0000",
    "host": "localhost",
    "port": "5432"
}

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocer360 Authentication")
        self.root.geometry("700x700")
        self.root.iconbitmap("assets/myIcon.ico")
      
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.username_entry = None
        self.password_entry = None
        self.role_var = None
        
        self.initialize_login_ui()

        
    def verify_login(self, username, password, role):
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

    def log_out(self, username):
        try:
            conn = psycopg2.connect(**conn_details)
            cursor = conn.cursor()
            cursor.execute("UPDATE signers SET logged_in = %s WHERE user_name = %s", (False, username))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Logged Out", "You have successfully logged out.")
            self.initialize_login_ui()
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", "Failed to log out. Please try again.")

    def sign_in(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if self.verify_login(username, password, role):
            if role == "admin":
                AdminDashboard(self.root, username, self.log_out)
            else:
                UserDashboard(self.root, username, self.log_out)
                
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")


    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
   
    
    def initialize_login_ui(self):
        self.clear_screen()
        self.root.geometry("800x600")
        
        
        # Create frames for left and right sides
        left_frame = ctk.CTkFrame(self.root, width=300, height=700)
        left_frame.pack(side="left", fill="both", expand=True)

        right_frame = ctk.CTkFrame(self.root, width=300, height=700)
        right_frame.pack(side="right", fill="both", expand=True)
        

        # Add background image to the left frame
        self.load_background_image(left_frame)

        # Add login form to the right frame
        self.load_logo_image(right_frame)
        ctk.CTkLabel(right_frame, text="User Name", font=("Helvetica", 16)).pack(pady=10)
        self.username_entry = ctk.CTkEntry(right_frame, placeholder_text="Enter your ID", width=250)
        self.username_entry.pack(pady=10)

        ctk.CTkLabel(right_frame, text="Password", font=("Helvetica", 16)).pack(pady=10)
        self.password_entry = ctk.CTkEntry(right_frame, show='*', placeholder_text="Enter your password", width=250)
        self.password_entry.pack(pady=10)

        self.role_var = StringVar(value="user")
        ctk.CTkLabel(right_frame, text="Role", font=("Helvetica", 16)).pack(pady=10)
        ctk.CTkSegmentedButton(right_frame, variable=self.role_var, values=["admin", "user"]).pack(pady=5)

        ctk.CTkButton(right_frame, text="Login", command=self.sign_in, width=200, height=40, corner_radius=10).pack(pady=10)
        
        
        # ctk.CTkButton(right_frame, text="Face Sign-In", command=lambda: FaceSignIn(self.root, UserDashboard, self.log_out), width=200, height=40, corner_radius=10).pack(pady=10)
        #-------
        icon_image = Image.open("assets/camera.png")
        icon_photo = ImageTk.PhotoImage(icon_image)
        
        icon_button = ctk.CTkButton(
            master=right_frame,
            image=icon_photo,
            text="",  # No text, just the icon
            command=lambda: FaceSignIn(self.root, UserDashboard, self.log_out),
            # command=lambda: FaceSignIn(self.root, SupermarketManagementApp, self.log_out),
            width=50, 
            height=40, 
            corner_radius=10,
            fg_color="transparent",  # Make the button transparent
            hover_color="#DCA9EB"  # Optional: Change color on hover
        )
        icon_button.pack(pady=10)
        #-------
        
    def load_background_image(self, frame):
        try:
            my_image = ctk.CTkImage(light_image=Image.open("assets/background.png"), size=(400, 700))
            image_label = ctk.CTkLabel(frame, image=my_image, text="")
            image_label.image = my_image  # Keep a reference to avoid garbage collection
            image_label.pack(fill="both", expand=True)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
    def load_logo_image(self, frame):
        try:
            my_image = ctk.CTkImage(light_image=Image.open("assets/logo.png"), size=(100, 100))
            image_label = ctk.CTkLabel(frame, image=my_image, text="")
            image_label.image = my_image  # Keep a reference to avoid garbage collection
            image_label.pack(fill="both", expand=True)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
                
    



if __name__ == "__main__":
    root = ctk.CTk()
    app = MainApplication(root)
    root.mainloop()

