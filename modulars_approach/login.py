import os
import cv2
from datetime import datetime
from strictApp import App
# login.py in modulars_approach

import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
import util

import uuid
import psycopg2

class Login(App):
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
        
    
    def run(self):
        super().run()
        
    # def __del__(self):
    #     if self.cap:
    #         self.cap.release()

if __name__ == "__main__":
    app = Login()
    app.run()