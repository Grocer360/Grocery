import customtkinter as ctk

class BasePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure_design()

    def configure_design(self):
        # Common design elements using customtkinter methods
        self.configure(fg_color="#2c3e50")  # Example background color
        self.label_style = {"font": ("Helvetica", 18)}

    def add_label(self, text):
        label = ctk.CTkLabel(self, text=text, **self.label_style)
        label.pack(pady=20)
        return label

