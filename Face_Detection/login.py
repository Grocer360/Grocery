import os
import cv2
import face_recognition
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import numpy as np
import psycopg2
import sys

# Configuration
config = {
    "camera_index": 0,
    "db_dir": "./Face_Detection/db",
    "log_path": "./Face_Detection/logentry.txt",
    "window_size": "1200x520+350+100"
}

conn_details = {
    'dbname': "okzegkwz",
    'user': "okzegkwz",
    'password': "7UwFflnPy3byudSr32K1ugHniRSVK6v_",
    'host': "kandula.db.elephantsql.com",
    'port': "5432"
}

# Load known faces from database
def load_known_faces(db_dir):
    known_encodings = []
    known_names = []

    if not os.listdir(db_dir):
        messagebox.showwarning("No Data", "The database directory is empty. Please add face images.")
        raise ValueError("The database directory is empty.")

    for file_name in os.listdir(db_dir):
        if file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png"):
            image_path = os.path.join(db_dir, file_name)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_encodings.append(encoding[0])
                known_names.append(os.path.splitext(file_name)[0])

    if not known_encodings or not known_names:
        messagebox.showwarning("No Data", "No face encodings found in the database directory. Please add valid face images.")
        raise ValueError("No face encodings found in the database directory.")

    return known_encodings, known_names


# Log access
def log_access(username):
    """ Log the access time in the log file and database. """
    # Log to the file
    with open(config["log_path"], "a") as log_file:
        log_file.write(f"User {username} logged in at {datetime.now()}\n")

    # Log to the database
    log_to_db(username)

def log_to_db(username):
    """ Log the access time to the PostgreSQL database. """
    try:
        current_time = datetime.now()
        conn = psycopg2.connect(**conn_details)
        cursor = conn.cursor()

        # Update the user's login status and time
        cursor.execute("""
            UPDATE Users
            SET logged_in = %s, time_stamp_in = %s
            WHERE user_name = %s
        """, (True, current_time, username))
        conn.commit()
        print(f"Login time logged for {username} at {current_time}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error logging login time: {e}")

# Compare faces
def compare_faces(known_encodings, face_encoding):
    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)
    return matches[best_match_index], best_match_index

# Main App
class FaceRecognitionApp(ctk.CTk):
    def __init__(self, parent=None):
        super().__init__()

        self.known_encodings, self.known_names = load_known_faces(config["db_dir"])

        if parent is not None:
            self.parent = parent
            self.withdraw()  # Hide the main window
            self.top = ctk.CTkToplevel(self.parent)
            self.top.title("Face Recognition Login")
            self.top.geometry("800x600")
        else:
            self.top = self

        self.geometry("800x600")
        self.title("Face Recognition Login")

        self.camera_label = ctk.CTkLabel(self.top, text="")
        self.camera_label.pack(pady=20)

        self.capture_button = ctk.CTkButton(self.top, text="Capture Image", command=self.on_capture)
        self.capture_button.pack(pady=20)

        self.result_label = ctk.CTkLabel(self.top, text="")
        self.result_label.pack(pady=20)

        self.cap = cv2.VideoCapture(0)  # Change 0 to your camera index if needed
        self.update_camera_feed()

    def on_capture(self):
        try:
            # Capture a frame from the camera
            ret, frame = self.cap.read()
            if ret:
                print("Frame captured successfully")
                
                # Convert the frame to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                print("Converted frame to RGB")
                
                # Find face locations in the frame
                face_locations = face_recognition.face_locations(rgb_frame)
                print(f"Found {len(face_locations)} face(s) in the frame")
                
                if face_locations:
                    # Get the encoding for the first detected face
                    face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                    print("Face encoding generated")
                    
                    # Compare the detected face with known faces
                    match, index = self.compare_faces(face_encoding)
                    if match:
                        username = self.known_names[index]
                        log_access(username)
                        self.result_label.configure(text=f"Welcome {username}!")
                        print(f"Recognized face as {username}")
                        
                        # Show a messagebox for successful login
                        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
                    else:
                        self.result_label.configure(text="Face not recognized.")
                        print("Face not recognized")
                        
                        # Show a messagebox for face not recognized
                        messagebox.showwarning("Not Recognized", "Face not recognized.")
                else:
                    self.result_label.configure(text="No face detected.")
                    print("No face detected in the frame")
                    
                    # Show a messagebox for no face detected
                    messagebox.showwarning("No Face Detected", "No face detected. Please try again.")
            else:
                print("Failed to capture frame from camera")
                self.result_label.configure(text="Failed to capture image.")
        except Exception as e:
            print(f"Error during face recognition: {e}")
            self.result_label.configure(text=f"Error: {str(e)}")

    def compare_faces(self, face_encoding):
        matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
        face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        return matches[best_match_index], best_match_index

    def update_camera_feed(self):
        """ Continuously update the camera feed on the GUI. """
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        self.camera_label.after(10, self.update_camera_feed)  # Refresh the feed every 10ms

if __name__ == "__main__":
    app = FaceRecognitionApp()
    app.mainloop()
