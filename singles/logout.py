# logout.py

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import os
import psycopg2
from config import Config, get_db_connection
import util

class LogoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Logout")
        self.root.geometry("800x600")

        self.config = Config()
        self.db_dir = self.config.get('db_dir', './db')
        self.webcam_label = util.get_img_label(self.root, width=600, height=400)

        self.logout_button = util.get_button(self.root, 'Logout', '#333333', self.logout)

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

            self.most_recent_capture_arr = frame
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=img_pil)

            self.webcam_label.imgtk = imgtk
            self.webcam_label.configure(image=imgtk)
            self.root.after(20, self.process_webcam)
        except Exception as e:
            print(f"Error processing webcam: {e}")

    def logout(self):
        if self.most_recent_capture_arr is None:
            util.msg_box("Error", "No image captured for logout")
            return

        recognized_name = util.recognize(self.most_recent_capture_arr, self.db_dir)

        if recognized_name in ['unknown_person', 'no_persons_found', 'error']:
            util.msg_box("Error", "Face not recognized. Please try again.")
        else:
            util.msg_box("Goodbye!", f"Goodbye, {recognized_name}")
            self.log_access("Logout", recognized_name)

    def log_access(self, action, username):
        try:
            conn = get_db_connection()
            if conn is None:
                util.msg_box("Error", "Cannot connect to the database.")
                return

            cursor = conn.cursor()
            current_time = datetime.now()

            cursor.execute("""
                SELECT time_stamp_in FROM Users WHERE user_name = %s AND logged_in = %s
            """, (username, True))
            row = cursor.fetchone()
            if row:
                time_stamp_in = row[0]
                working_duration = util.calculate_working_hours(time_stamp_in, current_time)

                cursor.execute("""
                    UPDATE Users
                    SET logged_in = %s, time_stamp_out = %s, work_duration = %s
                    WHERE user_name = %s
                """, (False, current_time, working_duration, username))
                conn.commit()

                print(f"Logout time logged for {username} at {current_time} with working duration of {working_duration:.2f} hours")

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error logging logout time: {e}")
            util.msg_box("Error", "Failed to log logout time. Please try again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogoutApp(root)
    root.mainloop()
