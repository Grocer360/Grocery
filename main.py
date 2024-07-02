import os
import tkinter as tk
from tkinter import simpledialog, messagebox
import cv2
from PIL import Image, ImageTk
import datetime
import subprocess
import util
import numpy as np
import json
import uuid

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
        self.config = Config()
        self.main_window = tk.Tk()
        self.main_window.geometry(self.config.get('window_size', "1200x520+350+100"))
        self.main_window.title("Face Attendance System")

        self.login_button_main_window = util.get_button(self.main_window, 'Login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=200)

        self.logout_button_main_window = util.get_button(self.main_window, 'Logout', 'red', self.logout)
        self.logout_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'Register New User', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)
        
        # Manage Users Button
        self.manage_users_button_main_window = util.get_button(self.main_window, 'Manage Users', 'blue', self.manage_users)
        self.manage_users_button_main_window.place(x=750, y=500)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

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
            util.msg_box('Error', 'No face detected. Please try again.')
            return

        unknown_img_path = os.path.join(os.getcwd(), 'unknown_img.jpg')

        rgb_frame = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB).astype('uint8')
        cv2.imwrite(unknown_img_path, rgb_frame)

        recognized_name = self.recognize_user(unknown_img_path)
        os.remove(unknown_img_path)

        if recognized_name in ['unknown person', 'unknown', 'no persons found']:
            util.msg_box("Error", "Unknown user. Please register new user or try again.")
        else:
            registered_users = self.list_registered_users()
            if recognized_name not in registered_users:
                util.msg_box("Error", "You are not registered. Please register first.")
            else:
                util.msg_box("Welcome back!", f"Welcome {recognized_name}")
                self.log_event(recognized_name, 'in')

    def logout(self):
        if self.most_recent_capture_arr is None:
            print("No image captured for logout")
            return

        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) == 0:
            util.msg_box('Error', 'No face detected. Please try again.')
            return

        unknown_img_path = os.path.join(os.getcwd(), 'unknown_img.jpg')

        rgb_frame = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB).astype('uint8')
        cv2.imwrite(unknown_img_path, rgb_frame)

        recognized_name = self.recognize_user(unknown_img_path)
        os.remove(unknown_img_path)

        if recognized_name in ['unknown person', 'unknown', 'no persons found']:
            util.msg_box('Ups...', 'Unknown user. Please register new user or try again.')
        else:
            registered_users = self.list_registered_users()
            if recognized_name not in registered_users:
                util.msg_box("Error", "You are not registered. Please register first.")
            else:
                util.msg_box('Goodbye!', f'Goodbye, {recognized_name}.')
                self.log_event(recognized_name, 'out')

    def register_new_user(self):
        if self.cap is None:
            print("Camera not initialized!")
            return

        if self.register_new_user_window and self.register_new_user_window.winfo_exists():
            self.register_new_user_window.deiconify()
            return

        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label()

        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Please, \ninput username:')
        self.text_label_register_new_user.place(x=750, y=70)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self):
        if self.cap is None:
            print("Camera not initialized!")
            return

        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame from camera")
            return

        frame = frame.astype('uint8')  # Ensure frame is in uint8 format

        self.register_new_user_capture = frame  # Store the captured frame for registration

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)

        self.capture_label.imgtk = imgtk
        self.capture_label.configure(image=imgtk)

    def accept_register_new_user(self):
        if self.register_new_user_capture is None:
            print("No image captured for registration")
            return

        faces = self.detect_face(self.register_new_user_capture)
        if len(faces) == 0:
            util.msg_box('Error', 'No face detected. Please try again.')
            return

        name = self.entry_text_register_new_user.get(1.0, "end-1c").strip()
        if not name:
            util.msg_box('Error', 'Username cannot be empty.')
            return

        file_path = os.path.join(self.db_dir, f'{name}.jpg')
        if os.path.exists(file_path):
            util.msg_box('Error', 'User already exists. Please choose a different name.')
            return

        cv2.imwrite(file_path, self.register_new_user_capture.astype('uint8'))  # Ensure image is uint8

        util.msg_box('Success!', 'User was registered successfully!')

        self.register_new_user_window.destroy()

    def log_event(self, name, event_type):
        with open(self.log_path, 'a') as f:
            f.write(f'{name},{datetime.datetime.now()},{event_type}\n')

    def list_registered_users(self):
        registered_users = [f.split('.')[0] for f in os.listdir(self.db_dir) if f.endswith('.jpg')]
        return registered_users

    def update_selected_user(self):
        selected_user = self.selected_user_var.get()
        if selected_user:
            new_name = simpledialog.askstring("Input", f"Enter new name for {selected_user}:")
            if new_name:
                os.rename(os.path.join(self.db_dir, f'{selected_user}.jpg'), os.path.join(self.db_dir, f'{new_name}.jpg'))
                util.msg_box('Success!', f'Username updated to {new_name}.')
            else:
                util.msg_box('Error', 'Name update cancelled or invalid input.')

    def delete_selected_user(self):
        selected_user = self.selected_user_var.get()
        if selected_user:
            os.remove(os.path.join(self.db_dir, f'{selected_user}.jpg'))
            util.msg_box('Success!', f'User {selected_user} has been deleted.')

    def manage_users(self):
        if self.manage_users_window and self.manage_users_window.winfo_exists():
            self.manage_users_window.deiconify()
            return

        self.manage_users_window = tk.Toplevel(self.main_window)
        self.manage_users_window.geometry("600x400+400+150")

        self.selected_user_var = tk.StringVar(self.manage_users_window)

        registered_users = self.list_registered_users()
        if registered_users:
            self.selected_user_var.set(registered_users[0])  # Default to the first user in the list

        user_dropdown = tk.OptionMenu(self.manage_users_window, self.selected_user_var, *registered_users)
        user_dropdown.pack(pady=20)

        update_button = util.get_button(self.manage_users_window, 'Update Name', 'blue', self.update_selected_user)
        update_button.pack(pady=10)

        delete_button = util.get_button(self.manage_users_window, 'Delete User', 'red', self.delete_selected_user)
        delete_button.pack(pady=10)

        close_button = util.get_button(self.manage_users_window, 'Close', 'gray', self.manage_users_window.destroy)
        close_button.pack(pady=10)

    def start(self):
        self.main_window.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()