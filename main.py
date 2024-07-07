import os
import customtkinter as ctk  # Change import from tkinter to customtkinter
from tkinter import simpledialog, messagebox
import cv2
from PIL import Image, ImageTk
import datetime
import subprocess
import util  # Import util that now uses customtkinter
import numpy as np
import json
import uuid
import face_recognition
import pickle
import re
import logging
import psycopg2
logging.basicConfig(level=logging.DEBUG)

# Config Class to handle configuration
class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = os.path.join(os.path.dirname(__file__), config_file)
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Configuration file {self.config_file} not found.")
            self.config = {}

    def get(self, key, default=None):
        return self.config.get(key, default)

class App:
    def __init__(self):
        self.conn_details = {
            'dbname': "okzegkwz",
            'user': "okzegkwz",
            'password': "7UwFflnPy3byudSr32K1ugHniRSVK6v_",
            'host': "kandula.db.elephantsql.com",
            'port': "5432"
        }
        self.config = Config()
        self.main_window = ctk.CTk()  # Use ctk.CTk() for the main window
        self.main_window.geometry(self.config.get('window_size', "1200x520+350+100"))
        self.main_window.title("Face Attendance System")

        # Grid configuration
        self.main_window.grid_rowconfigure(0, weight=1)
        self.main_window.grid_columnconfigure(0, weight=1)
        self.main_window.grid_columnconfigure(1, weight=1)

        # Webcam label
        self.webcam_label = util.get_img_label(self.main_window, width=900, height=700)  # Increased width and height
        self.webcam_label.grid(row=0, column=0, rowspan=5, padx=(10, 0), pady=10)  # Place in the first column

        # Buttons
        button_padx = 10
        button_pady = 10

        self.login_button_main_window = util.get_button(self.main_window, 'Login', '#4286f4', self.login)
        self.login_button_main_window.grid(row=0, column=1, padx=button_padx, pady=button_pady, sticky='n')

        self.logout_button_main_window = util.get_button(self.main_window, 'Logout', '#333333', self.logout)
        self.logout_button_main_window.grid(row=1, column=1, padx=button_padx, pady=button_pady, sticky='n')

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'Register New User', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.grid(row=2, column=1, padx=button_padx, pady=button_pady, sticky='n')

        self.manage_users_button_main_window = util.get_button(self.main_window, 'Manage Users', 'blue', self.manage_users)
        self.manage_users_button_main_window.grid(row=3, column=1, padx=button_padx, pady=button_pady, sticky='n')

        self.db_dir = self.config.get('db_dir', './db')
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = self.config.get('log_path', './log.txt')

        self.cap = None
        self.most_recent_capture_arr = None  # Store the most recent frame
        self.start_camera()

        self.register_new_user_window = None  # To track if the window is already open
        self.manage_users_window = None  # To track if the window is already open

    def start_camera(self):
        if self.cap is None:
            try:
                self.cap = cv2.VideoCapture(self.config.get('camera_index', 0))  # Change the index if needed
                self.process_webcam()
            except Exception as e:
                print(f"Error starting camera: {e}")

    def start_camera(self):
        if self.cap is None:
            try:
                self.cap = cv2.VideoCapture(self.config.get('camera_index', 0))  # Change the index if needed
                self.process_webcam()
            except Exception as e:
                print(f"Error starting camera: {e}")
        
    def process_webcam(self):
        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("Failed to capture frame from camera")
                self.main_window.after(100, self.process_webcam)
                return
            frame = frame.astype('uint8')  # Convert to uint8 format
            self.most_recent_capture_arr = frame  # Update this with the most recent frame

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=img_pil)

            self.webcam_label.imgtk = imgtk
            self.webcam_label.configure(image=imgtk)

            self.main_window.after(20, self.process_webcam)  # Schedule next frame update
        except Exception as e:
            print(f"Error processing webcam: {e}")

    def detect_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces

    def recognize_user(self, image_path):
        try:
            output = subprocess.check_output(['face_recognition', self.db_dir, image_path]).decode('utf-8')
            print(f"Face recognition output: {output}")  # Debugging line to check the output format
            lines = output.strip().split("\n")
            name_line = lines[0] if lines else ""
            name_parts = name_line.split(",")
            recognized_name = name_parts[1] if len(name_parts) > 1 else "unknown"
            return recognized_name.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running face_recognition command: {e}")
            return "unknown"

    def login(self):
        if self.most_recent_capture_arr is None:
            print("No image captured for login")
            return

        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) == 0:
            print("No faces detected in the captured frame")
            util.msg_box("Error", "No faces detected!")
            return

        # Save the captured image temporarily for face recognition
        img_path = os.path.join(self.db_dir, f"temp_login_{uuid.uuid4().hex}.jpg")
        cv2.imwrite(img_path, self.most_recent_capture_arr)
        
        recognized_name = util.recognize(self.most_recent_capture_arr, self.db_dir)
        
        if recognized_name == 'unknown_person':
            util.msg_box("Error", "Face not recognized. Please try again.")
        elif recognized_name == 'no_persons_found':
            util.msg_box("Error", "No persons found. Please try again.")
        else:
            util.msg_box("Welcome!", f"Hello, {recognized_name}")
            self.log_access("Login", recognized_name)

        # Clean up temporary file
        os.remove(img_path)

    def logout(self):
        if self.most_recent_capture_arr is None:
            print("No image captured for logout")
            return

        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) == 0:
            print("No faces detected in the captured frame")
            util.msg_box("Error", "No faces detected!")
            return

        # Save the captured image temporarily for face recognition
        img_path = os.path.join(self.db_dir, f"temp_logout_{uuid.uuid4().hex}.jpg")
        cv2.imwrite(img_path, self.most_recent_capture_arr)
        
        recognized_name = util.recognize(self.most_recent_capture_arr, self.db_dir)
        
        if recognized_name == 'unknown_person':
            util.msg_box("Error", "Face not recognized. Please try again.")
        elif recognized_name == 'no_persons_found':
            util.msg_box("Error", "No persons found. Please try again.")
        else:
            util.msg_box("Goodbye!", f"Goodbye, {recognized_name}")
            self.log_access("Logout", recognized_name)

        # Clean up temporary file
        os.remove(img_path)

    def log_access(self, action, name):
        """
        Log the access details to a log file.
        """
        with open(self.log_path, 'a') as f:
            log_entry = f"{datetime.datetime.now()}: {name} {action}\n"
            f.write(log_entry)
            print(f"Log entry added: {log_entry}")

    def register_new_user(self):
        # Create a new window for registering a new user
        self.register_new_user_window = ctk.CTkToplevel(self.main_window)
        self.register_new_user_window.geometry("900x700+200+0")
        self.register_new_user_window.title("Register New User")

        # Configure grid layout for the registration window
        self.register_new_user_window.grid_rowconfigure(0, weight=1)
        self.register_new_user_window.grid_rowconfigure(1, weight=1)
        self.register_new_user_window.grid_columnconfigure(0, weight=1)
        self.register_new_user_window.grid_columnconfigure(1, weight=1)

        # Label for the name input
        name_label = util.get_text_label(self.register_new_user_window, "Enter Name:")
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

        # Entry widget for the name input
        self.name_entry = ctk.CTkEntry(self.register_new_user_window)
        self.name_entry.grid(row=0, column=1, padx=10, pady=0, sticky='w')

        # Label for the password input
        password_label = util.get_text_label(self.register_new_user_window, "Enter Password:")
        password_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

        # Entry widget for the password input
        self.password_entry = ctk.CTkEntry(self.register_new_user_window, show='*')
        self.password_entry.grid(row=1, column=1, padx=10, pady=0, sticky='w')

        # Webcam label to display the camera feed
        self.reg_webcam_label = util.get_img_label_grid(self.register_new_user_window, width=700, height=500)
        self.reg_webcam_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Capture button to capture and save the face
        capture_button = util.get_button(self.register_new_user_window, "Capture Face", "blue", self.capture_and_save_face)
        capture_button.grid(row=3, column=0, padx=10, pady=10, sticky='e')

        # Close button to close the registration window
        close_button = util.get_button(self.register_new_user_window, "Close", "red", self.register_new_user_window.destroy)
        close_button.grid(row=3, column=1, padx=10, pady=10, sticky='w')

        # Start the camera and display the feed in the registration window
        self.start_camera()
        self.process_webcam_registration()  # Start processing the webcam for the registration window

    def capture_and_save_face(self):
        """
        Capture the current frame from the webcam, detect the face, and save it along with the embeddings.
        """
        name = self.name_entry.get()  # Get the name from the entry widget
        print(name,self.password_entry.get())
        if not name:
            util.msg_box("Error", "Name cannot be empty!")
            return

        if self.most_recent_capture_arr is None:
            util.msg_box("Error", "No image captured!")
            return

        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) == 0:
            util.msg_box("Error", "No faces detected!")
            return

        # Save the captured face image
        face_img_path = os.path.join(self.db_dir, f"{name}.jpg")
        cv2.imwrite(face_img_path, self.most_recent_capture_arr)

        # Extract and save face embeddings
        # face_embeddings = face_recognition.face_encodings(self.most_recent_capture_arr)
        # if face_embeddings:
        #     embedding_path = os.path.join(self.db_dir, f"{name}.pickle")
        #     with open(embedding_path, 'wb') as f:
        #         pickle.dump(face_embeddings[0], f)

        face_embeddings = face_recognition.face_encodings(self.most_recent_capture_arr)
        if face_embeddings:
            # Convert the image to bytes
            image_bytes = pickle.dumps(self.most_recent_capture_arr)

            # Save the username, hashed password, and image path to the database
            try:
                conn = psycopg2.connect(**self.conn_details)
                cur = conn.cursor()

                # Insert user details into the database
                cur.execute("""
                    INSERT INTO users (user_name, password, role, working_hours, logged_in, img, time_stamp_in, time_stamp_out)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, self.password_entry.get(), "user", 0, False, image_bytes, datetime.datetime.now(), None))

                conn.commit()
                cur.close()
                conn.close()

                util.msg_box("Success", f"User {name} registered successfully!")
            except psycopg2.Error as e:
                print(f"Error inserting user into database: {e}")
                util.msg_box("Database Error", "Error registering user. Please try again later.")

        else:
            util.msg_box("Error", "Failed to encode face. Try again!")



    def is_valid_username(self, username):
            """
            Validate the username.
            Username should only contain alphanumeric characters and spaces, no special characters.
            """
            valid_username_pattern = re.compile(r'^[A-Za-z0-9 ]+$')
            return bool(valid_username_pattern.match(username))

    def is_unique_username(self, username):
        """
        Check if the username is unique in the database directory.
        """
        existing_files = os.listdir(self.db_dir)
        existing_usernames = [os.path.splitext(file)[0] for file in existing_files]
        return username not in existing_usernames



# Configure logging

    def capture_and_save_face(self):
        """
        Capture the current frame from the webcam, validate the username, and save the face image and embeddings.
        """
        name = self.name_entry.get().strip()
        logging.debug(f"Captured name: {name}")

        # Validate the username
        if not name:
            util.msg_box("Error", "Name cannot be empty!")
            logging.error("Name is empty")
            return

        if not self.is_valid_username(name):
            util.msg_box("Error", "Invalid name! Use only letters, numbers, and spaces.")
            logging.error(f"Invalid name: {name}")
            return

        if not self.is_unique_username(name):
            util.msg_box("Error", "This username already exists. Please choose a different one.")
            logging.error(f"Username already exists: {name}")
            return

        if self.most_recent_capture_arr is None:
            util.msg_box("Error", "No image captured!")
            logging.error("No image captured")
            return

        logging.debug("Processing face detection")
        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) == 0:
            util.msg_box("Error", "No faces detected!")
            logging.error("No faces detected")
            return

        face_img_path = os.path.join(self.db_dir, f"{name}.jpg")
        cv2.imwrite(face_img_path, self.most_recent_capture_arr)
        logging.debug(f"Saved face image to {face_img_path}")

        face_embeddings = face_recognition.face_encodings(self.most_recent_capture_arr)
        if face_embeddings:
            embedding_path = os.path.join(self.db_dir, f"{name}.pickle")
            with open(embedding_path, 'wb') as f:
                pickle.dump(face_embeddings[0], f)
            logging.debug(f"Saved face embeddings to {embedding_path}")

            util.msg_box("Success", f"User {name} registered successfully!")
        else:
            util.msg_box("Error", "Failed to encode face. Try again!")
            logging.error("Failed to encode face")

    def process_webcam_registration(self):
        """
        Continuously capture frames from the webcam and update the registration window.
        """
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Convert the frame to RGB (OpenCV uses BGR by default)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert the image to a PhotoImage
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                # Update the webcam label with the new image
                self.reg_webcam_label.imgtk = imgtk
                self.reg_webcam_label.configure(image=imgtk)
            self.reg_webcam_label.after(10, self.process_webcam_registration)
            
    def capture_and_save_face(self):
        """
        Capture the current frame from the webcam, validate inputs, detect the face, and save it along with the embeddings.
        """
        name = self.name_entry.get().strip()  # Get the name from the entry widget
        print(name,self.password_entry.get())

        # Validate inputs
        if not name:
            util.msg_box("Error", "Name cannot be empty!")
            return

        if self.most_recent_capture_arr is None:
            util.msg_box("Error", "No image captured!")
            return

        # Detect faces
        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) == 0:
            util.msg_box("Error", "No faces detected!")
            return

        # Save the captured face image
        face_img_path = os.path.join(self.db_dir, f"{name}.jpg")
        cv2.imwrite(face_img_path, self.most_recent_capture_arr)

        # Extract and save face embeddings
        face_embeddings = face_recognition.face_encodings(self.most_recent_capture_arr)
        if face_embeddings:
            embedding_path = os.path.join(self.db_dir, f"{name}.pickle")
            with open(embedding_path, 'wb') as f:
                pickle.dump(face_embeddings[0], f)

            # Save user details to the database
            try:
                conn = psycopg2.connect(**self.conn_details)
                cur = conn.cursor()

                cur.execute("""
                    INSERT INTO users (user_name, password, role, working_hours, logged_in, img, time_stamp_in, time_stamp_out)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, self.password_entry.get(), "user", 0, False, image_bytes, datetime.datetime.now(), None))

                conn.commit()
                cur.close()
                conn.close()

                util.msg_box("Success", f"User {name} registered successfully!")
            except psycopg2.Error as e:
                print(f"Error inserting user into database: {e}")
                util.msg_box("Database Error", "Error registering user. Please try again later.")

        else:
            util.msg_box("Error", "Failed to encode face. Try again!")



    def manage_users(self):

        self.manage_users_window = ctk.CTkToplevel(self.main_window)
        self.manage_users_window.geometry("400x300")
        self.manage_users_window.title("Manage Users")

        # Reset window tracking variable when closed
        self.manage_users_window.protocol("WM_DELETE_WINDOW", self.on_close_manage_window)

        # Display registered users and provide options to remove them
        registered_users = sorted(os.listdir(self.db_dir))

        for user_file in registered_users:
            user_name = os.path.splitext(user_file)[0]
            user_label = util.get_text_label(self.manage_users_window, user_name)
            user_label.pack(pady=5)

            delete_button = util.get_button(self.manage_users_window, "Delete", "red",
                                            lambda user_file=user_file: self.delete_user(user_file))
            delete_button.pack(pady=5)

        close_button = util.get_button(self.manage_users_window, "Close", "red",
                                       self.manage_users_window.destroy)
        close_button.pack(pady=10)

    def delete_user(self, user_file):
        user_path = os.path.join(self.db_dir, user_file)
        if os.path.exists(user_path):
            os.remove(user_path)
            util.msg_box("Success", f"User {user_file} deleted successfully!")
            self.manage_users_window.destroy()
            self.manage_users()  # Refresh the manage users window
            
            
    def on_close_manage_window(self):
        """
        Handle the closing of the manage users window.
        """
        self.manage_users_window.destroy()
        self.manage_users_window = None



    def run(self):
        self.main_window.mainloop()
        
    def __del__(self):
        if self.cap:
            self.cap.release()

if __name__ == "__main__":
    app = App()
    app.run()