import os
import cv2
import face_recognition
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from datetime import datetime
import numpy as np

config = {
    "camera_index": 0,
    "db_dir": "./db",
    "log_path": "./log.txt",
    "window_size": "1200x520+350+100"
}

def load_known_faces(db_dir):
    known_encodings = []
    known_names = []
    for file_name in os.listdir(db_dir):
        if file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png"):
            image_path = os.path.join(db_dir, file_name)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_encodings.append(encoding[0])
                known_names.append(os.path.splitext(file_name)[0])
    return known_encodings, known_names

known_encodings, known_names = load_known_faces(config["db_dir"])

def log_access(username):
    with open(config["log_path"], "a") as log_file:
        log_file.write(f"User {username} logged in at {datetime.now()}\n")

def capture_image(camera_index):
    cap = cv2.VideoCapture(camera_index)
    ret, frame = cap.read()
    cap.release()
    if ret:
        return frame
    else:
        raise RuntimeError("Failed to capture image")

def compare_faces(known_encodings, face_encoding):
    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)
    return matches[best_match_index], best_match_index

class FaceRecognitionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.geometry(config["window_size"])
        self.title("Face Recognition Login")

        self.camera_label = ctk.CTkLabel(self, text="Camera Feed")
        self.camera_label.pack(pady=20)

        self.capture_button = ctk.CTkButton(self, text="Capture Image", command=self.on_capture)
        self.capture_button.pack(pady=20)

        self.result_label = ctk.CTkLabel(self, text="")
        self.result_label.pack(pady=20)

        self.cap = cv2.VideoCapture(config["camera_index"])
        self.update_camera_feed()

    def on_capture(self):
        try:
            ret, frame = self.cap.read()
            if ret:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                if face_locations:
                    face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                    match, index = compare_faces(known_encodings, face_encoding)
                    if match:
                        username = known_names[index]
                        log_access(username)
                        self.result_label.configure(text=f"Welcome {username}!")
                        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
                    else:
                        self.result_label.configure(text="Face not recognized.")
                else:
                    self.result_label.configure(text="No face detected.")
            else:
                self.result_label.configure(text="Failed to capture image.")
        except Exception as e:
            self.result_label.configure(text=f"Error: {str(e)}")

    def update_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            self.imgtk = ctk.CTkImage(img, size=(self.camera_label.winfo_width(), self.camera_label.winfo_height()))
            self.camera_label.configure(image=self.imgtk)
        self.camera_label.after(10, self.update_camera_feed)

def run_face_recognition_app():
    app = FaceRecognitionApp()
    app.mainloop()


if __name__ == "__main__":
    app = FaceRecognitionApp()
    app.mainloop()