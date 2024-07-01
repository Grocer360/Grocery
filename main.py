import os
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import datetime
import subprocess
import util
import numpy as np
import uuid 


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")
        self.main_window.title("Face Attendance System")

        self.login_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=200)

        self.logout_button_main_window = util.get_button(self.main_window, 'logout', 'red', self.logout)
        self.logout_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'

        self.cap = None
        self.most_recent_capture_arr = None  # Add this to store the most recent frame
        self.start_camera()

    def start_camera(self):
        if self.cap is None:
            try:
                self.cap = cv2.VideoCapture(0)  # Change the index (0, 1, 2, etc.) if needed
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

    def login(self):

        unknown_img_path = os.path.join(os.getcwd(), 'unknown_img.jpg')

        # Ensure the image is in RGB format before saving
        rgb_frame = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB).astype('uint8')
        cv2.imwrite(unknown_img_path, rgb_frame)

        try:
            output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
            name = output.split(',')[1][:-3]
            if name in ['unknown person', 'no persons found']:
                util.msg_box("Error", "Unknown user. Please register new user or try again.")
            else:
                util.msg_box("Welcome back!", f"Welcome {name}")
                with open(self.log_path, 'a') as f:
                    f.write('{}, {}, {}\n'.format(name, 'in', datetime.datetime.now()))
        except subprocess.CalledProcessError as e:
            print(f"Error running face_recognition command: {e}")
            util.msg_box("Error", "There was an error processing the image. Please try again.")
        finally:
            os.remove(unknown_img_path)


    def logout(self):
        

        unknown_img_path = os.path.join(os.getcwd(), 'unknown_img.jpg')

        if self.cap is None:
            print("Camera not initialized!")
            return

        ret, frame = self.cap.read()
        if not ret or frame is None:
            print("Failed to capture frame from camera")
            return

        # Ensure the image is in RGB format before saving
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype('uint8')
        cv2.imwrite(unknown_img_path, rgb_frame)

        try:
            output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
            name = output.split(',')[1][:-3]

            if name in ['unknown_person', 'no_persons_found']:
                util.msg_box('Ups...', 'Unknown user. Please register new user or try again.')
            else:
                util.msg_box('Goodbye!', f'Goodbye, {name}.')
                with open(self.log_path, 'a') as f:
                    f.write('{}, {}, {}\n'.format(name, 'out', datetime.datetime.now()))
        except subprocess.CalledProcessError as e:
            print(f"Error running face_recognition command: {e}")
            util.msg_box("Error", "There was an error processing the image. Please try again.")
        finally:
            os.remove(unknown_img_path)

    def register_new_user(self):
        if self.cap is None:
            print("Camera not initialized!")
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
        ret, frame = self.cap.read()
        if not ret or frame is None:
            print("Failed to capture frame from camera")
            return

        self.register_new_user_capture = frame.copy()

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)

        self.capture_label.imgtk = imgtk
        self.capture_label.configure(image=imgtk)

    def accept_register_new_user(self):
        if self.register_new_user_capture is None:
            print("No image captured for registration")
            return

        name = self.entry_text_register_new_user.get(1.0, "end-1c")

        file_path = os.path.join(self.db_dir, f'{name}.jpg')
        cv2.imwrite(file_path, self.register_new_user_capture.astype('uint8'))  # Ensure image is uint8

        util.msg_box('Success!', 'User was registered successfully!')

        self.register_new_user_window.destroy()

    def log_event(self, name, event_type):
        with open(self.log_path, 'a') as f:
            f.write(f'{name},{datetime.datetime.now()},{event_type}\n')

    def start(self):
        self.main_window.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
