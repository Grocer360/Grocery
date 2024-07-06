# main.py

import os
import customtkinter as ctk  # Change import from tkinter to customtkinter
from tkinter import simpledialog, messagebox
import cv2
from PIL import Image, ImageTk
# import datetime
from datetime import datetime
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
import hashlib
from io import BytesIO
import io
import zlib
import base64
# import tkinter.filedialog as filedialog
# import shutil

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
        self.main_window.title("Face ID Authentication System")

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

            try:
                current_time = datetime.now()
                conn = psycopg2.connect(**self.conn_details)
                cursor = conn.cursor()

                # Update the user's login status and time
                cursor.execute("""
                    UPDATE Users
                    SET logged_in = %s, time_stamp_in = %s
                    WHERE user_name = %s
                """, (True, current_time, recognized_name))
                conn.commit()
                print(f"Login time logged for {recognized_name} at {current_time}")

                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error logging login time: {e}")
                util.msg_box("Error", "Failed to log login time. Please try again.")

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

        try:
            recognized_name = util.recognize(self.most_recent_capture_arr, self.db_dir)
            print(f"Recognized name: {recognized_name}")

            if recognized_name == 'unknown_person':
                util.msg_box("Error", "Face not recognized. Please try again.")
            elif recognized_name == 'no_persons_found':
                util.msg_box("Error", "No persons found. Please try again.")
            else:
                # Calculate working hours
                time_stamp_in = self.get_login_time(recognized_name)  # Retrieve login time from database
                print(f"Login time for {recognized_name}: {time_stamp_in}")
                time_stamp_out = datetime.now()  # Current time is logout time
                print(f"Logout time for {recognized_name}: {time_stamp_out}")

                if time_stamp_in:
                    working_hours = self.calculate_working_hours(time_stamp_in, time_stamp_out)
                else:
                    print(f"Failed to retrieve login time for {recognized_name}")
                    working_hours = "N/A"

                # Update database
                success = self.update_logout_status(recognized_name, time_stamp_out, working_hours)

                if success:
                    util.msg_box("Goodbye!", f"Goodbye, {recognized_name}")
                    self.log_access("Logout", recognized_name)
                else:
                    util.msg_box("Error", "Failed to update logout status. Please try again.")
        finally:
            # Clean up temporary file
            if os.path.exists(img_path):
                os.remove(img_path)


    def get_login_time(self, username):
        try:
            conn = psycopg2.connect(**self.conn_details)
            cursor = conn.cursor()
            cursor.execute("SELECT time_stamp_in FROM Users WHERE user_name = %s", (username,))
            time_stamp_in = cursor.fetchone()
            cursor.close()
            conn.close()
            if time_stamp_in:
                return time_stamp_in[0]
            return None
        except Exception as e:
            print(f"Error retrieving login time for {username}: {e}")
            return None

    def calculate_working_hours(self, time_stamp_in, time_stamp_out):
        try:
            duration = time_stamp_out - time_stamp_in
            hours = duration.total_seconds() / 3600
            working_hours = f"{duration}"
            return working_hours
        except Exception as e:
            print(f"Error calculating working hours: {e}")
            return "N/A"

    def update_logout_status(self, username, time_stamp_out, working_hours):
        try:
            with psycopg2.connect(**self.conn_details) as conn:
                with conn.cursor() as cursor:
                    # Print the details being updated for debugging
                    print(f"Updating logout status for {username}")
                    print(f"Set logged_in to False, time_stamp_out to {time_stamp_out}, working_hours to {working_hours}")

                    cursor.execute("""
                        UPDATE Users 
                        SET logged_in = %s, time_stamp_out = %s, working_hours = %s 
                        WHERE user_name = %s
                    """, (False, time_stamp_out, working_hours, username))
                    
                    # Check how many rows were affected by the update
                    rows_updated = cursor.rowcount
                    print(f"Rows updated: {rows_updated}")

                    # Commit the transaction
                    conn.commit()

                    if rows_updated > 0:
                        print(f"Logout details updated for {username}")
                        return True
                    else:
                        print(f"No records updated. User {username} may not exist or is already logged out.")
                        return False
        except psycopg2.DatabaseError as db_error:
            print(f"Database error updating logout status for {username}: {db_error}")
        except psycopg2.OperationalError as op_error:
            print(f"Operational error updating logout status for {username}: {op_error}")
        except Exception as e:
            print(f"Unexpected error updating logout status for {username}: {e}")
        return False


    def verify_login(self,username, password, role):
        try:
            conn = psycopg2.connect(**self.conn_details)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE user_name = %s AND password = %s AND role = %s", (username, password, role))
            user = cursor.fetchone()
            if user:
                current_time = datetime.datetime.now()
                cursor.execute("UPDATE Users SET logged_in = %s, time_stamp_in = %s WHERE user_name = %s", (True, current_time, username))
                conn.commit()
            cursor.close()
            conn.close()
            return user is not None
        except Exception as e:
            print(f"Error: {e}")

    


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

    def register_new_user(self):
        # Create a new window for registering a new user
        self.register_new_user_window = ctk.CTkToplevel(self.main_window)
        self.register_new_user_window.geometry("900x700")
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
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        # Label for the password input
        password_label = util.get_text_label(self.register_new_user_window, "Enter Password:")
        password_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

        # Entry widget for the password input
        self.password_entry = ctk.CTkEntry(self.register_new_user_window, show='*')
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        # Label for the role selection
        role_label = util.get_text_label(self.register_new_user_window, "Select Role:")
        role_label.grid(row=2, column=0, padx=10, pady=10, sticky='e')

        # Dropdown menu for role selection
        self.role_var = ctk.StringVar(value="user")  # Default value
        role_dropdown = ctk.CTkOptionMenu(self.register_new_user_window, variable=self.role_var, values=["admin", "user"])
        role_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        # Webcam label to display the camera feed
        self.reg_webcam_label = util.get_img_label_grid(self.register_new_user_window, width=700, height=500)
        self.reg_webcam_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Capture button to capture and save the face
        capture_button = util.get_button(self.register_new_user_window, "Capture Face", "blue",
                                        lambda: self.capture_and_save_face())
        capture_button.grid(row=4, column=0, padx=10, pady=10, sticky='e')

        # Close button to close the registration window
        close_button = util.get_button(self.register_new_user_window, "Close", "red",
                                    self.register_new_user_window.destroy)
        close_button.grid(row=4, column=1, padx=10, pady=10, sticky='w')

        # Start the camera and display the feed in the registration window
        self.start_camera()
        self.process_webcam_registration()

  # Start processing the webcam for the registration window


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


    def is_unique_username(self, username):
        try:
            conn = psycopg2.connect(**self.conn_details)
            cursor = conn.cursor()
            cursor.execute("SELECT user_name FROM Users WHERE user_name = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is None
        except Exception as e:
            logging.error(f"Database error: {e}")
            return False
    def compress_and_encode_image(self,image_data):
    # Assuming image_data is a BytesIO object or similar containing the image
        with Image.open(image_data) as img:
            with io.BytesIO() as img_buffer:
                img.save(img_buffer, format='JPEG')
                img_data = img_buffer.getvalue()
        
        compressed_data = zlib.compress(img_data)
        encoded_data = base64.b64encode(compressed_data).decode('utf-8')
        return encoded_data
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

    def manage_users(self):
        # Create the manage users window
        self.manage_users_window = ctk.CTkToplevel(self.main_window)
        self.manage_users_window.geometry("515x200")
        self.manage_users_window.title("Manage Users")
        self.manage_users_window.resizable(False, False)

        # Reset window tracking variable when closed
        self.manage_users_window.protocol("WM_DELETE_WINDOW", self.on_close_manage_window)

        # Get registered users
        registered_users = sorted(os.listdir(self.db_dir))
        
        # Filter to only show .jpg files (assuming the users are stored as .jpg and .pickle)
        image_files = [f for f in registered_users if f.endswith('.jpg')]
        
        # Extract user names from image files (remove the extension)
        user_names = [os.path.splitext(f)[0] for f in image_files]
        
        if user_names:
            selected_user = ctk.StringVar(value=user_names[0])  # Default to the first user

            user_dropdown = ctk.CTkOptionMenu(self.manage_users_window, variable=selected_user, values=user_names)
            user_dropdown.grid(row=0, column=1, columnspan=2, pady=10, padx=10, sticky="ew")

            # Add an entry field for the new name
            new_name_entry = ctk.CTkEntry(self.manage_users_window, placeholder_text="Enter new name")
            new_name_entry.grid(row=1, column=1, columnspan=2, pady=10, padx=10, sticky="ew")

            # Define common padding and button size
            button_padx = 5  # Padding between buttons
            button_width = 100  # Button width in pixels
            button_height = 30  # Button height in pixels

            # Add the buttons and place them horizontally on the same row
            update_name_button = util.get_button_grid(
                self.manage_users_window, 
                "Update Name", 
                "blue", 
                lambda: self.update_user_name(selected_user.get(), new_name_entry.get()),
                fg="white",
                width=button_width, 
                height=button_height
            )
            update_name_button.grid(row=2, column=0, padx=button_padx, pady=10, sticky="ew")

            update_image_button = util.get_button_grid(
                self.manage_users_window, 
                "Update Image (Capture New)", 
                "green", 
                lambda: self.start_capture_new_image(selected_user.get()),
                fg="white",
                width=button_width, 
                height=button_height
            )
            update_image_button.grid(row=2, column=1, padx=button_padx, pady=10, sticky="ew")

            delete_button = util.get_button_grid(
                self.manage_users_window, 
                "Delete", 
                "red", 
                lambda: self.delete_user(selected_user.get()),
                fg="white",
                width=button_width, 
                height=button_height
            )
            delete_button.grid(row=2, column=2, padx=button_padx, pady=10, sticky="ew")

            close_button = util.get_button_grid(
                self.manage_users_window, 
                "Close", 
                "gray", 
                self.manage_users_window.destroy,
                fg="white",
                width=button_width, 
                height=button_height
            )
            close_button.grid(row=2, column=3, padx=button_padx, pady=10, sticky="ew")
        else:
            # If no users are found, display a message
            no_users_label = util.get_text_label(self.manage_users_window, "No users found!")
            no_users_label.grid(row=0, column=0, columnspan=4, pady=20, padx=10, sticky="ew")

            close_button = util.get_button_grid(
                self.manage_users_window, 
                "Close", 
                "gray", 
                self.manage_users_window.destroy,
                fg="white",
                width=button_width, 
                height=button_height
            )
            close_button.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        self.main_window.wait_window(self.manage_users_window)

    def update_user_name(self, old_name, new_name):
        """
        Update the user's name and rename their associated files.
        """
        if not new_name:
            util.msg_box("Error", "New name cannot be empty!")
            return

        # Define the old and new file paths
        old_image_file = os.path.join(self.db_dir, f"{old_name}.jpg")
        new_image_file = os.path.join(self.db_dir, f"{new_name}.jpg")

        old_encoding_file = os.path.join(self.db_dir, f"{old_name}.pickle")
        new_encoding_file = os.path.join(self.db_dir, f"{new_name}.pickle")

        try:
            # Rename the image file
            if os.path.exists(old_image_file):
                os.rename(old_image_file, new_image_file)
            else:
                util.msg_box("Error", f"Image file for {old_name} not found!")

            # Rename the encoding file
            if os.path.exists(old_encoding_file):
                os.rename(old_encoding_file, new_encoding_file)
            else:
                util.msg_box("Error", f"Encoding file for {old_name} not found!")

            util.msg_box("Success", f"User {old_name} renamed to {new_name} successfully!")

        except Exception as e:
            util.msg_box("Error", f"An error occurred: {e}")

        # Refresh the manage users window
        self.manage_users_window.destroy()
        self.manage_users()

    def update_user_name(self, old_name, new_name):
        """
        Update the user's name and rename their associated files.
        """
        new_name = new_name.strip()

        # Validate the new name
        if not new_name:
            util.msg_box("Error", "New name cannot be empty!")
            return

        if not self.is_valid_username(new_name):
            util.msg_box("Error", "Invalid name! Use only letters, numbers, and spaces.")
            return

        if not self.is_unique_username(new_name):
            util.msg_box("Error", "This username already exists. Please choose a different one.")
            return

        # Define the old and new file paths
        old_image_file = os.path.join(self.db_dir, f"{old_name}.jpg")
        new_image_file = os.path.join(self.db_dir, f"{new_name}.jpg")

        old_encoding_file = os.path.join(self.db_dir, f"{old_name}.pickle")
        new_encoding_file = os.path.join(self.db_dir, f"{new_name}.pickle")

        try:
            # Rename the image file
            if os.path.exists(old_image_file):
                os.rename(old_image_file, new_image_file)
            else:
                util.msg_box("Error", f"Image file for {old_name} not found!")
                return

            # Rename the encoding file
            if os.path.exists(old_encoding_file):
                os.rename(old_encoding_file, new_encoding_file)
            else:
                util.msg_box("Error", f"Encoding file for {old_name} not found!")
                return

            util.msg_box("Success", f"User {old_name} renamed to {new_name} successfully!")

        except Exception as e:
            util.msg_box("Error", f"An error occurred: {e}")

        # Refresh the manage users window
        self.manage_users_window.destroy()
        self.manage_users()

    def start_capture_new_image(self, user_name):
        """
        Initialize the process to capture a new image for updating a user's profile.
        """
        self.capture_user_name = user_name  # Store the user's name for whom the image is being updated

        # Create a new window for capturing the new image
        self.capture_image_window = ctk.CTkToplevel(self.main_window)
        self.capture_image_window.geometry("900x600")
        self.capture_image_window.title(f"Capture New Image for {user_name}")

        # Configure grid layout for the capture window
        self.capture_image_window.grid_rowconfigure(0, weight=1)
        self.capture_image_window.grid_columnconfigure(0, weight=1)
        self.capture_image_window.grid_columnconfigure(1, weight=1)

        # Webcam label to display the camera feed
        self.capture_webcam_label = util.get_img_label_grid(self.capture_image_window, width=700, height=500)
        self.capture_webcam_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Capture button to capture and save the face
        capture_button = util.get_button(self.capture_image_window, "Capture Image", "blue",
                                        self.capture_and_save_new_image)
        capture_button.grid(row=1, column=0, padx=10, pady=10, sticky='e')

        # Close button to close the capture window
        close_button = util.get_button(self.capture_image_window, "Close", "red",
                                    self.capture_image_window.destroy)
        close_button.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        # Start the camera and display the feed in the capture window
        self.start_camera()
        self.process_webcam_capture()  # Start processing the webcam for the capture window

    def process_webcam_capture(self):
        """
        Continuously capture frames from the webcam and update the capture window.
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
                self.capture_webcam_label.imgtk = imgtk
                self.capture_webcam_label.configure(image=imgtk)
            self.capture_webcam_label.after(10, self.process_webcam_capture)

    def capture_and_save_new_image(self):
        """
        Capture the current frame from the webcam and save it as the user's new image.
        """
        if self.most_recent_capture_arr is None:
            util.msg_box("Error", "No image captured!")
            logging.error("No image captured")
            return

        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) == 0:
            util.msg_box("Error", "No faces detected!")
            logging.error("No faces detected")
            return

        user_name = self.capture_user_name
        face_img_path = os.path.join(self.db_dir, f"{user_name}.jpg")
        cv2.imwrite(face_img_path, self.most_recent_capture_arr)
        logging.debug(f"Saved new face image to {face_img_path}")

        face_embeddings = face_recognition.face_encodings(self.most_recent_capture_arr)
        if face_embeddings:
            embedding_path = os.path.join(self.db_dir, f"{user_name}.pickle")
            with open(embedding_path, 'wb') as f:
                pickle.dump(face_embeddings[0], f)
            logging.debug(f"Updated face embeddings for {user_name}")

            util.msg_box("Success", f"Image for {user_name} updated successfully!")
        else:
            util.msg_box("Error", "Failed to encode face. Try again!")
            logging.error("Failed to encode face")

        # Close the capture window
        self.capture_image_window.destroy()
        # Refresh the manage users window
        self.manage_users_window.destroy()
        self.manage_users()


    def delete_user(self, user_name):
        # Construct the paths for the image and encoding file
        image_file = os.path.join(self.db_dir, f"{user_name}.jpg")
        encoding_file = os.path.join(self.db_dir, f"{user_name}.pickle")

        # Delete the image file if it exists
        if os.path.exists(image_file):
            os.remove(image_file)
            print(f"Deleted {image_file}")

        # Delete the encoding file if it exists
        if os.path.exists(encoding_file):
            os.remove(encoding_file)
            print(f"Deleted {encoding_file}")

        # Show a success message
        util.msg_box("Success", f"User {user_name} deleted successfully!")

        # Close the manage users window and refresh it
        self.manage_users_window.destroy()
        self.manage_users()  # Reopen the manage users window to refresh the list

            
            
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
