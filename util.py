import os
import pickle
import tkinter as tk
from tkinter import messagebox
import face_recognition

# UI Utility Functions

def get_button(window, text, color, command, fg='white', font=('Helvetica bold', 20), height=1, width=20):
    """
    Create a Tkinter button with the specified parameters.

    Args:
    window (tk.Tk or tk.Toplevel): Parent window.
    text (str): Button text.
    color (str): Background color of the button.
    command (function): Function to call when the button is pressed.
    fg (str, optional): Foreground color of the button text. Default is 'white'.
    font (tuple, optional): Font style and size. Default is ('Helvetica bold', 20).
    height (int, optional): Height of the button. Default is 2.
    width (int, optional): Width of the button. Default is 20.

    Returns:
    tk.Button: Configured button widget.
    """
    button = tk.Button(
        window,
        text=text,
        activebackground="black",
        activeforeground="white",
        fg=fg,
        bg=color,
        command=command,
        height=height,
        width=width,
        font=font
    )
    return button

def get_img_label(window, row=0, column=0):
    """
    Create a Tkinter label to display images.

    Args:
    window (tk.Tk or tk.Toplevel): Parent window.
    row (int, optional): Row position for grid layout. Default is 0.
    column (int, optional): Column position for grid layout. Default is 0.

    Returns:
    tk.Label: Configured label widget.
    """
    label = tk.Label(window)
    label.grid(row=row, column=column)
    return label

def get_text_label(window, text, font=("sans-serif", 21), justify="left"):
    """
    Create a Tkinter label for displaying text.

    Args:
    window (tk.Tk or tk.Toplevel): Parent window.
    text (str): Text to display in the label.
    font (tuple, optional): Font style and size. Default is ("sans-serif", 21).
    justify (str, optional): Justification of the text. Default is "left".

    Returns:
    tk.Label: Configured label widget.
    """
    label = tk.Label(window, text=text)
    label.config(font=font, justify=justify)
    return label

def get_entry_text(window, height=2, width=15, font=("Arial", 32)):
    """
    Create a Tkinter text entry widget.

    Args:
    window (tk.Tk or tk.Toplevel): Parent window.
    height (int, optional): Height of the text entry. Default is 2.
    width (int, optional): Width of the text entry. Default is 15.
    font (tuple, optional): Font style and size. Default is ("Arial", 32).

    Returns:
    tk.Text: Configured text entry widget.
    """
    inputtxt = tk.Text(window,
                       height=height,
                       width=width,
                       font=font)
    return inputtxt

def msg_box(title, description, msg_type='info'):
    """
    Display a message box with the specified title and description.

    Args:
    title (str): Title of the message box.
    description (str): Message to display.
    msg_type (str, optional): Type of the message box. Can be 'info', 'warning', or 'error'. Default is 'info'.
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

    Args:
    db_path (str): Path to the directory containing embeddings files.

    Returns:
    list: List of embeddings.
    list: List of corresponding user names.
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

    Args:
    img (numpy.ndarray): Image containing the face to recognize.
    db_path (str): Path to the directory containing embeddings files.

    Returns:
    str: The recognized user name or 'unknown_person' if no match is found.
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
