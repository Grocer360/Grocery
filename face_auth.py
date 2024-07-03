import customtkinter as ctk
from tkinter import messagebox

class FaceSignIn:
    def __init__(self, root, open_user_dashboard, log_out):
        self.root = root
        self.open_user_dashboard = open_user_dashboard
        self.log_out = log_out
        self.show_face_signin()

    def show_face_signin(self):
        face_signin_window = ctk.CTkToplevel(self.root)
        face_signin_window.title("Face Sign-In")
        face_signin_window.geometry("400x300")
        face_signin_window.lift()
        face_signin_window.focus_force()
        face_signin_window.grab_set()

        ctk.CTkLabel(face_signin_window, text="Face Sign-In", font=("Helvetica", 20)).pack(pady=20)
        ctk.CTkButton(face_signin_window, text="Simulate Face Sign-In", command=self.face_signin_success, width=200, height=40, corner_radius=10).pack(pady=20)

    def face_signin_success(self):
        messagebox.showinfo("Face Sign-In", "Face sign-in successful!")
        self.open_user_dashboard(self.root, "user", self.log_out)


