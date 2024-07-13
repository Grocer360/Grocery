import tkinter as tk
import customtkinter as ctk
ctk.set_appearance_mode("dark")
import cv2
import face_recognition
from PIL import Image, ImageTk
import os
import psycopg2
import re
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
        self.root.geometry("662x700")
        self.root.configure(bg='#333333')
        self.root.resizable(False, False)
        
        self.config = Config()
        self.db_dir = self.config.get('db_dir', './Face_Detection/db')
        self.webcam_label = util.get_img_label(self.root, width=600, height=400)
        self.webcam_label.grid(row=0, column=0, columnspan=2, pady=20, padx=10)

        # Create a frame to hold both the username and password inputs
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.grid(row=1, column=0, columnspan=2, pady=20, padx=10)

        self.role_label = util.get_text_label(self.input_frame, text="")
        self.role_label.grid(row=0, column=0, padx=5)

        self.role_var = ctk.StringVar(value="user")
        self.role_dropdown = ctk.CTkOptionMenu(self.input_frame, variable=self.role_var, values=["admin", "user"])
        self.role_dropdown.grid(row=0, column=1, padx=5)

        self.username_label = util.get_text_label(self.input_frame, text="")
        self.username_label.grid(row=0, column=2, padx=5)

        self.username_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Username")
        self.username_entry.grid(row=0, column=3, padx=5)
        self.username_entry.bind("<KeyRelease>", self.validate_username)

        self.password_label = util.get_text_label(self.input_frame, text="")
        self.password_label.grid(row=0, column=4, padx=5)

        self.password_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Password", show='*')
        self.password_entry.grid(row=0, column=5, padx=5)

        self.capture_image_button = util.get_button(self.root, 'Capture Image', '#00796b', self.capture_image)
        self.capture_image_button.grid(row=2, column=0, pady=10)

        self.save_user_button = util.get_button(self.root, 'Sign Up', '#00796b', self.save_user)
        self.save_user_button.grid(row=2, column=1, pady=10)

        self.cap = None
        self.most_recent_capture_arr = None
        self.captured_image_displayed = False
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
            if self.captured_image_displayed:
                self.root.after(20, self.process_webcam)
                return

            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.root.after(100, self.process_webcam)
                return

            frame = frame.astype('uint8')
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

        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)

        # Detect faces in the image
        face_locations = face_recognition.face_locations(rgb_frame)
        if len(face_locations) == 0:
            util.msg_box("Error", "No faces detected. Please try again.")
            return

        # Draw green rectangles around detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(self.most_recent_capture_arr, (left, top), (right, bottom), (0, 255, 0), 2)

        user_img_dir = os.path.join(self.db_dir)
        if not os.path.exists(user_img_dir):
            os.makedirs(user_img_dir)

        img_path = os.path.join(user_img_dir, f"{username}.jpg")
        cv2.imwrite(img_path, self.most_recent_capture_arr)
        util.msg_box("Info", "Successfully captured")

        self.captured_image_displayed = True
        img_rgb = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        self.webcam_label.imgtk = imgtk
        self.webcam_label.configure(image=imgtk)

        password = self.password_entry.get()
        role = self.role_var.get()

        if not username:
            util.msg_box("Error", "Please enter a username.")
            return

        if not password or len(password) < 6:
            util.msg_box("Error", "Password must be at least 6 characters long.")
            return

        img_path = os.path.join(self.db_dir, f"{username}.jpg")
        if not os.path.exists(img_path):
            util.msg_box("Error", "Please capture an image first.")
            return

        if not self.is_unique_username(username):
            util.msg_box("Error", "Username already exists. Please choose a different one.")
            return




    def detect_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces

    def save_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not username:
            util.msg_box("Error", "Please enter a username.")
            return

        if not password or len(password) < 6:
            util.msg_box("Error", "Password must be at least 6 characters long.")
            return

        img_path = os.path.join(self.db_dir, f"{username}.jpg")
        if not os.path.exists(img_path):
            util.msg_box("Error", "Please capture an image first.")
            return

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

        self.captured_image_displayed = False
        self.process_webcam()

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

    def validate_username(self, event):
        username = self.username_entry.get()
        if not re.match("^[a-zA-Z0-9]*$", username):
            self.username_entry.delete(0, tk.END)
            util.msg_box("Error", "Username can only contain letters and numbers.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RegisterUserApp(root)
    root.mainloop()