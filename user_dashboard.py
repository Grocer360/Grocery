

import customtkinter as ctk

class UserDashboard:
    def __init__(self, root, username, log_out):
        self.root = root
        self.username = username
        self.log_out = log_out
        self.initialize_user_dashboard()

    def initialize_user_dashboard(self):
        self.clear_screen()
        ctk.CTkLabel(self.root, text="User Dashboard", font=("Helvetica", 20)).pack(pady=20)
        self.create_dashboard_buttons([("Log Out", lambda: self.log_out(self.username))])

    def create_dashboard_buttons(self, buttons):
        for text, command in buttons:
            ctk.CTkButton(self.root, text=text, command=command, width=200, height=40, corner_radius=10).pack(pady=10)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


