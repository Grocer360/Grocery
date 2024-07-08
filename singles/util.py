# util.py

import customtkinter as ctk
import os
import pickle
from tkinter import messagebox
import face_recognition

# UI Utility Functions

def get_button(root, text, color, command, fg='white'):
    button = ctk.CTkButton(root, text=text, fg_color=color, command=command, text_color=fg)
    button.pack(padx=10, pady=10)
    return button
# util.py

def get_button_grid(parent, text, bg_color, command, fg="white", width=None, height=None):
    button = ctk.CTkButton(
        parent, 
        text=text, 
        fg_color=bg_color, 
        text_color=fg, 
        command=command,
        width=width,  # Set width if provided
        height=height  # Set height if provided
    )
    return button

def get_img_label(window, width=700, height=500):
    """
    Create a CustomTkinter label to display images with specified width and height.
    """
    label = ctk.CTkLabel(window, width=width, height=height)
    label.pack(pady=10)  # Use pack instead of grid
    return label
def get_img_label_grid(window, width, height):
    """
    Create a label for displaying images.
    """
    label = ctk.CTkLabel(window, width=width, height=height)  # Create the label with specified width and height
    label.grid(sticky='nsew')  # Use grid instead of pack and make it expand in all directions
    return label

def get_text_label(window, text, font=("sans-serif", 21), justify="left"):
    """
    Create a CustomTkinter label for displaying text.
    """
    label = ctk.CTkLabel(window, text=text, font=ctk.CTkFont(*font))
    return label

def get_entry_text(window, height=2, width=15, font=("Arial", 32)):
    """
    Create a CustomTkinter entry widget.
    """
    inputtxt = ctk.CTkTextbox(
        window,
        height=height * 20,  # Adjusted height for CTkTextbox
        width=width * 20,    # Adjusted width for CTkTextbox
        font=ctk.CTkFont(*font)
    )
    return inputtxt

def msg_box(title, description, msg_type='info'):
    """
    Display a message box with the specified title and description.
    """
    if msg_type == 'info':
        messagebox.showinfo(title, description)
    elif msg_type == 'warning':
        messagebox.showwarning(title, description)
    elif msg_type == 'error':
        messagebox.showerror(title, description)

# Face Recognition Utility Functions

def load_embeddings(db_path):
    """
    Load face embeddings from a specified directory.
    """
    embeddings_list = []
    names_list = []
    for filename in sorted(os.listdir(db_path)):
        path_ = os.path.join(db_path, filename)
        try:
            with open(path_, 'rb') as file:
                embeddings = pickle.load(file)
                embeddings_list.append(embeddings)
                names_list.append(filename[:-7])  # Assuming filename ends with '.pickle'
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return embeddings_list, names_list

def recognize(img, db_path):
    """
    Recognize a face from an image against a database of embeddings.
    """
    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found'
    else:
        embeddings_unknown = embeddings_unknown[0]

    embeddings_list, names_list = load_embeddings(db_path)

    matches = face_recognition.compare_faces(embeddings_list, embeddings_unknown)

    if any(matches):
        match_index = matches.index(True)
        return names_list[match_index]
    else:
        return 'unknown_person'