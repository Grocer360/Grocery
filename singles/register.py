# register_user.py

import tkinter as tk
import customtkinter as ctk
ctk.set_appearance_mode("dark")
import cv2
from PIL import Image, ImageTk
import os
import psycopg2
from config import Config, get_db_connection
import util
import logging

class RegisterUserApp:
    def __init__(self, root):
        self.conn_details = {
        'dbname': "okzegkwz",
        'user': "okzegkwz",
        'password': "7UwFflnPy3byudSr32K1ugHniRSVK6v_",
        'host': "kandula.db.elephantsql.com",
        'port': "5432"
    }
        self.root = root
        self.root.title("Register New User")
        self.root.geometry("800x650")
        self.root.configure(bg='#333333')
        self.root.resizable(False, False)
        
        self.config = Config()
        self.db_dir = self.config.get('db_dir', './db')
        self.webcam_label = util.get_img_label(self.root, width=600, height=400)

        # Create a frame to hold both the username and password inputs
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.pack(pady=20, padx=10)
        
        self.role_label = util.get_text_label(self.input_frame, text="")
        self.role_label.pack(side=ctk.LEFT, padx=0)
        
        self.role_var = ctk.StringVar(value="user")  # Default role
        self.role_dropdown = ctk.CTkOptionMenu(self.input_frame, variable=self.role_var, values=["admin", "user"])
        self.role_dropdown.pack(side=ctk.LEFT, padx=10)
        
        # Create and pack the username label and entry into the frame
        self.username_label = util.get_text_label(self.input_frame, text="")
        self.username_label.pack(side=ctk.LEFT, padx=10)

        self.username_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Username")
        self.username_entry.pack(side=ctk.LEFT, padx=10)

        # Create and pack the password label and entry into the frame
        self.password_label = util.get_text_label(self.input_frame, text="")
        self.password_label.pack(side=ctk.LEFT, padx=10)

        self.password_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Password", show='*')
        self.password_entry.pack(side=ctk.LEFT, padx=10)

        # Button for capturing image
        self.capture_image_button = util.get_button(self.root, 'Capture Image', '#00796b', self.capture_image)
        self.capture_image_button.pack(pady=10)

        # # Button for saving user
        # self.save_user_button = util.get_button(self.root, 'Save User', '#00796b', self.save_user)
        # self.save_user_button.pack(pady=10)

        self.cap = None
        self.most_recent_capture_arr = None
        self.start_camera()

    def start_camera(self):
        if self.cap is None:
            try:
                self.cap = cv2.VideoCapture(self.config.get('camera_index', 0))
                self.process_webcam()
            except Exception as e:
                print(f"Error starting camera: {e}")

    def process_webcam(self):
        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.root.after(100, self.process_webcam)
                return

            # Convert the frame to uint8 format (required for OpenCV operations)
            frame = frame.astype('uint8')

            # Update the most recent frame with the current frame
            self.most_recent_capture_arr = frame
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=img_pil)

            self.webcam_label.imgtk = imgtk
            self.webcam_label.configure(image=imgtk)
            self.root.after(20, self.process_webcam)
        except Exception as e:
            print(f"Error processing webcam: {e}")

    def capture_image(self):
        if self.most_recent_capture_arr is None:
            util.msg_box("Error", "No image captured")
            return

        username = self.username_entry.get()
        if not username:
            util.msg_box("Error", "Please enter a username before capturing the image.")
            return

        # Check if a face is detected before saving the image
        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) == 0:
            util.msg_box("Error", "No faces detected. Please try again.")
            return

        user_img_dir = os.path.join(self.db_dir)
        if not os.path.exists(user_img_dir):
            os.makedirs(user_img_dir)

        img_path = os.path.join(user_img_dir, f"{username}.jpg")
        cv2.imwrite(img_path, self.most_recent_capture_arr)
        util.msg_box("Success", f"Image for {username} captured successfully.")
        
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not username:
            util.msg_box("Error", "Please enter a username.")
            return

        if not password or len(password) < 6:
            util.msg_box("Error", "Password must be at least 6 characters long.")
            return

        # Ensure the image has been captured
        img_path = os.path.join(self.db_dir, f"{username}.jpg")
        if not os.path.exists(img_path):
            util.msg_box("Error", "Please capture an image first.")
            return

        # Check if the username is unique
        if not self.is_unique_username(username):
            util.msg_box("Error", "Username already exists. Please choose a different one.")
            return

        try:
            conn = psycopg2.connect(**self.conn_details)
            if conn is None:
                util.msg_box("Error", "Cannot connect to the database.")
                print("Cannot connect to the database.")
                return

            cursor = conn.cursor()

            # Insert new user into the database
            cursor.execute("""
                INSERT INTO Users (user_name, password, role, logged_in, img)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, password, role, False, img_path))
            conn.commit()

            cursor.close()
            conn.close()

            util.msg_box("Success", f"User {username} registered successfully.")
        except Exception as e:
            print(f"Error saving new user: {e}")
            util.msg_box("Error", "Failed to register new user. Please try again.")

    def detect_face(self, frame):
        """
        Detects faces in the given frame using Haar cascade classifier.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces

    def is_unique_username(self, username):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_name FROM Users WHERE user_name = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is None
        except Exception as e:
            logging.error(f"Database error: {e}")
            return False

    # def save_user(self):
    #     username = self.username_entry.get()
    #     password = self.password_entry.get()
    #     role = self.role_var.get()

    #     if not username:
    #         util.msg_box("Error", "Please enter a username.")
    #         return

    #     if not password or len(password) < 6:
    #         util.msg_box("Error", "Password must be at least 6 characters long.")
    #         return

    #     # Ensure the image has been captured
    #     img_path = os.path.join(self.db_dir, f"{username}.jpg")
    #     if not os.path.exists(img_path):
    #         util.msg_box("Error", "Please capture an image first.")
    #         return

    #     # Check if the username is unique
    #     if not self.is_unique_username(username):
    #         util.msg_box("Error", "Username already exists. Please choose a different one.")
    #         return

    #     try:
    #         conn = psycopg2.connect(**self.conn_details)
    #         if conn is None:
    #             util.msg_box("Error", "Cannot connect to the database.")
    #             print("Cannot connect to the database.")
    #             return

    #         cursor = conn.cursor()

    #         # Insert new user into the database
    #         cursor.execute("""
    #             INSERT INTO Users (user_name, password, role, logged_in, img)
    #             VALUES (%s, %s, %s, %s, %s)
    #         """, (username, password, role, False, img_path))
    #         conn.commit()

    #         cursor.close()
    #         conn.close()

    #         util.msg_box("Success", f"User {username} registered successfully.")
    #     except Exception as e:
    #         print(f"Error saving new user: {e}")
    #         util.msg_box("Error", "Failed to register new user. Please try again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RegisterUserApp(root)
    root.mainloop()
