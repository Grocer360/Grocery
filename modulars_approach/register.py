
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import os

import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
import util

import logging
import psycopg2
import io
import zlib
import base64
from strictApp import App
class Register:
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
print("done")