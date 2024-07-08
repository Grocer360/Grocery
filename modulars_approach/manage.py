import os
import customtkinter as ctk  # Change import from tkinter to customtkinter
import cv2

import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
import util

import face_recognition
import pickle
import logging

class Manage:
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