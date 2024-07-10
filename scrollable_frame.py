import tkinter as tk
import customtkinter as ctk
from tkinter import ttk

class ScrollableFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        canvas = tk.Canvas(self)
        scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Configure scrollable_frame to expand
        scrollable_frame.grid_rowconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(0, weight=1)

        self.scrollable_frame = scrollable_frame

# Test the ScrollableFrame in a main window
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("600x400")

    frame = ScrollableFrame(root)
    frame.pack(fill="both", expand=True)

    # Add some content to the scrollable frame for testing
    for i in range(50):
        label = ctk.CTkLabel(frame.scrollable_frame, text=f"Label {i+1}")
        label.grid(row=i, column=0, pady=5, padx=5)

    root.mainloop()
