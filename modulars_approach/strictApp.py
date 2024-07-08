
import os
import customtkinter as ctk 
ctk.set_appearance_mode("dark")
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import subprocess

import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
import util


import face_recognition
import pickle
import re
import logging
import psycopg2
import hashlib
from logout import *
# from login import *
from config import *
from database import *
# from register import *
from manage import *



logging.basicConfig(level=logging.DEBUG)
class App:
    def __init__(self):
        self.config = Config()
        self.main_window = ctk.CTk()  # Use ctk.CTk() for the main window
        self.main_window.geometry(self.config.get('window_size', "1200x520+350+100"))
        self.main_window.title("Face ID Authentication System")

        # Configure the grid for the main window
        
        # The weight parameter determines how much extra space the row or column
        # should take up when the main window is resized. A weight of 1 indicates
        # that the row or column should take up an equal amount of extra space.
        # In this case, we want the main content (the webcam label) to take up
        # the most space, so we set the weight for the row and column that it's in
        # to 1. This means that the webcam label will expand to fill any extra
        # space in the window.
        #
        # The rowconfigure and columnconfigure methods are used to configure the
        # grid for the main window. They take two arguments: the index of the row
        # or column to configure, and the weight for that row or column.
        #
        # The first rowconfigure call configures the row that the webcam label is
        # in. The index is 0, and the weight is 1.
        self.main_window.grid_rowconfigure(0, weight=1)
        
        # The second rowconfigure call configures the column that the webcam label
        # is in. The index is 0, and the weight is 1.
        self.main_window.grid_columnconfigure(0, weight=1)
        
        # The third columnconfigure call configures the column that the buttons
        # are in. The index is 1, and the weight is 1.
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
        
        
    def log_access(self, action, name):
        """
        Log the access details to a log file.
        """
        try:
            # Retrieve log path from configuration or default to './log.txt'
            self.log_path = self.config.get('log_path', './log.txt')

            # Convert log_path to an absolute path if it is not already
            self.log_path = os.path.abspath(self.log_path)
            
            # Ensure the log file's directory exists
            logs_dir = os.path.dirname(self.log_path)
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)

            # Write the log entry to the file
            with open(self.log_path, 'a') as f:
                current_time = datetime.now()  # Get the current timestamp
                log_entry = f"{current_time}: {name} {action}\n"
                f.write(log_entry)
                print(f"Log entry added: {log_entry.strip()}")
        except Exception as e:
            print(f"Failed to log access: {e}")    
    
    def capture_and_save_face(self):
        name = self.name_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()  # Get the selected role
        logging.debug(f"Captured name: {name} with role: {role}")

        # Validate the username and password
        if not name or not password:
            util.msg_box("Error", "Name and password cannot be empty!")
            logging.error("Name or password is empty")
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

        # Convert the image to binary data
        img_bytes = bytes(self.most_recent_capture_arr)

        face_img_path = os.path.join(self.db_dir, f"{name}.jpg")
        cv2.imwrite(face_img_path, self.most_recent_capture_arr)
        logging.debug(f"Saved face image to {face_img_path}")
        print(face_img_path)
        face_embeddings = face_recognition.face_encodings(self.most_recent_capture_arr)
        if face_embeddings:
            embedding_path = os.path.join(self.db_dir, f"{name}.pickle")
            with open(embedding_path, 'wb') as f:
                pickle.dump(face_embeddings[0], f)
            logging.debug(f"Saved face embeddings to {embedding_path}")

            # Hash the password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Insert user data into the database
            try:
                conn = psycopg2.connect(**self.conn_details)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Users (user_name, password, role, img)
                    VALUES (%s, %s, %s, %s)
                """, (name, hashed_password, role, face_img_path))
                print(f"User {name} data inserted successfully!")
                conn.commit()
                cursor.close()
                conn.close()
                util.msg_box("Success", f"User {name} registered successfully!")
            except Exception as e:
                logging.error(f"Failed to insert user data into database: {e}")
                util.msg_box("Error", "Failed to register user. Try again!")
        else:
            util.msg_box("Error", "Failed to encode face. Try again!")
            logging.error("Failed to encode face")
    
    
    def calculate_working_hours(self, time_stamp_in, time_stamp_out):
        try:
            duration = time_stamp_out - time_stamp_in
            hours = duration.total_seconds() / 3600
            working_hours = f"{duration}"
            return working_hours
        except Exception as e:
            print(f"Error calculating working hours: {e}")
            return "N/A"
        
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
    
    def run(self):
        self.main_window.mainloop()
        
    def __del__(self):
        if self.cap:
            self.cap.release()
    