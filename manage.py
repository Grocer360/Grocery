import customtkinter as ctk
from tkinter import ttk, simpledialog, messagebox
import psycopg2
import re
import os
import cv2
from PIL import Image, ImageTk
import util
from config import Config, get_db_connection

class ManageUsersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Users")
        self.root.geometry("850x350")
        self.root.resizable(False, False)

        self.config = Config()
        self.db_dir = self.config.get('db_dir', './Face_Detection/db')
        self.cap = None
        self.most_recent_capture_arr = None
        self.capture_user_name = None

        # Create the Treeview for displaying users
        self.tree = ttk.Treeview(root)
        self.tree["columns"] = ("Username", "Role", "Image")
        self.tree.column("#0", width=0, stretch=ctk.NO)
        self.tree.heading("#0", text="", anchor=ctk.CENTER)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor=ctk.CENTER)
            self.tree.column(col, anchor=ctk.CENTER, width=200)

        self.tree.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        self.tree.bind('<ButtonRelease-1>', self.select_item)

        # Increase the Treeview font size
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        # Initialize selected user variable
        self.selected_user = None

        # Frame for buttons
        button_frame = ctk.CTkFrame(self.root)
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Add buttons for refreshing data, updating, and deleting users
        self.refresh_button = util.get_button(button_frame, 'Refresh Data', '#ff9800', self.load_data, row=0, column=0, padx=5)
        self.update_button = util.get_button(button_frame, 'Update User', '#4CAF50', self.update_user_window, row=0, column=1, padx=5)
        self.delete_button = util.get_button(button_frame, 'Delete User', '#f44336', self.delete_user, row=0, column=2, padx=5)
        self.update_image_button = util.get_button(button_frame, 'Update Image', '#2196F3', self.update_image_window, row=0, column=3, padx=5)

        # Frame for search entries
        search_frame = ctk.CTkFrame(self.root)
        search_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search", width=200)
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_entry.bind("<KeyRelease>", self.search_users)

        self.load_data()

    def load_data(self):
        self.clear_tree()

        try:
            conn = get_db_connection()
            if conn is None:
                util.msg_box("Error", "Cannot connect to the database.")
                return

            cursor = conn.cursor()
            cursor.execute("SELECT user_name, role, img FROM Users")
            rows = cursor.fetchall()

            for row in rows:
                self.tree.insert("", "end", values=row)

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error loading data: {e}")
            util.msg_box("Error", "Failed to load data. Please try again.")

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def select_item(self, event):
        item = self.tree.selection()
        self.selected_user = self.tree.item(item, "values") if item else None

        # Enable or disable buttons based on selection
        state = ctk.NORMAL if self.selected_user else ctk.DISABLED
        self.update_button.configure(state=state)
        self.delete_button.configure(state=state)
        self.update_image_button.configure(state=state)

    def update_user_window(self):
        if not self.selected_user:
            util.msg_box("Error", "No user selected for update.")
            return
            
        # Create the update user window
        self.update_window = ctk.CTkToplevel(self.root)
        self.update_window.title("Update User")
        self.update_window.geometry("300x170")
        self.update_window.resizable(False, False)

        ctk.CTkLabel(self.update_window, text="New Username:").grid(row=0, column=0, padx=10, pady=10)
        self.new_username_entry = ctk.CTkEntry(self.update_window)
        self.new_username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.new_username_entry.insert(0, self.selected_user[0])

        ctk.CTkLabel(self.update_window, text="New Role:").grid(row=1, column=0, padx=10, pady=10)
        self.new_role_combobox = ttk.Combobox(self.update_window, values=["user", "admin"], state="readonly")
        self.new_role_combobox.grid(row=1,rowspan=2, column=1,columnspan=2, padx=10, pady=10)
        self.new_role_combobox.set(self.selected_user[1])

        ctk.CTkButton(self.update_window, text="Update", command=self.update_user).grid(row=3, column=0, columnspan=2, pady=20)

    def update_user(self):
        new_name = self.new_username_entry.get()
        new_role = self.new_role_combobox.get()

        if not self.validate_user_input(new_name, new_role):
            return

        try:
            conn = get_db_connection()
            if conn is None:
                util.msg_box("Error", "Cannot connect to the database.")
                return

            cursor = conn.cursor()

            # Check if the new username already exists, excluding the current user
            if new_name != self.selected_user[0]:
                cursor.execute("SELECT COUNT(*) FROM Users WHERE user_name = %s", (new_name,))
                if cursor.fetchone()[0] > 0:
                    util.msg_box("Error", "Username already exists.")
                    return

            old_username = self.selected_user[0]
            old_img_path = os.path.join(self.config.get('db_dir'), f"{old_username}.jpg")
            new_img_path = os.path.join(self.config.get('db_dir'), f"{new_name}.jpg")

            # Update the database
            cursor.execute(
                "UPDATE Users SET user_name = %s, role = %s, img = %s WHERE user_name = %s",
                (new_name, new_role, new_img_path, old_username)
            )
            conn.commit()
            cursor.close()
            conn.close()

            # Rename the image file
            if os.path.exists(old_img_path):
                os.rename(old_img_path, new_img_path)

            util.msg_box("Success", "User updated successfully.")
            self.update_window.destroy()
            self.load_data()
        except Exception as e:
            print(f"Error updating user: {e}")
            util.msg_box("Error", "Failed to update user. Please try again.")

    def validate_user_input(self, username, role):
        if not username or not role:
            util.msg_box("Error", "Username and role cannot be empty.")
            return False

        if not re.match("^[a-zA-Z0-9_]+$", username):
            util.msg_box("Error", "Username can only contain letters, numbers, and underscores.")
            return False

        return True

    def delete_user(self):
        if not self.selected_user:
            util.msg_box("Error", "No user selected for deletion.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
            return

        try:
            conn = get_db_connection()
            if conn is None:
                util.msg_box("Error", "Cannot connect to the database.")
                return

            cursor = conn.cursor()
            username = self.selected_user[0]
            img_path = os.path.join(self.config.get('db_dir'), f"{username}.jpg")

            cursor.execute("DELETE FROM Users WHERE user_name = %s", (username,))
            conn.commit()
            cursor.close()
            conn.close()

            # Delete the image file
            if os.path.exists(img_path):
                os.remove(img_path)

            util.msg_box("Success", "User deleted successfully.")
            self.load_data()
        except Exception as e:
            print(f"Error deleting user: {e}")
            util.msg_box("Error", "Failed to delete user. Please try again.")

    def search_users(self, event):
        combined_search_text = self.search_entry.get().lower()
        print(f"Search text: {combined_search_text}")

        # First, reattach all items
        for item in self.tree.get_children():
            self.tree.detach(item)

        # Then, add only the matched items
        try:
            conn = get_db_connection()
            if conn is None:
                util.msg_box("Error", "Cannot connect to the database.")
                return

            cursor = conn.cursor()
            cursor.execute("SELECT user_name, role, img FROM Users")
            rows = cursor.fetchall()

            for row in rows:
                if combined_search_text in row[0].lower() or combined_search_text in row[1].lower():
                    self.tree.insert("", "end", values=row)

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error searching users: {e}")
            util.msg_box("Error", "Failed to search users. Please try again.")

    def update_image_window(self):
        if not self.selected_user:
            util.msg_box("Error", "No user selected to update image.")
            return

        self.capture_user_name = self.selected_user[0]

        self.capture_image_window = ctk.CTkToplevel(self.root)
        self.capture_image_window.title("Capture New Image")
        self.capture_image_window.geometry("550x500")
        self.capture_image_window.resizable(False, False)
        
        self.webcam_label = ctk.CTkLabel(self.capture_image_window)
        self.webcam_label.grid(row=0, column=0, padx=20, pady=20)

        capture_button = ctk.CTkButton(self.capture_image_window, text="Capture Image", command=self.capture_and_save_new_image)
        capture_button.grid(row=1, column=0, padx=20, pady=20)

        self.start_camera()

    def start_camera(self):
        if self.cap is None:
            try:
                self.cap = cv2.VideoCapture(self.config.get('camera_index', 0))  # Change the index if needed
                self.process_webcam()
            except Exception as e:
                print(f"Error starting camera: {e}")

    def process_webcam(self):
        """
        Continuously capture frames from the webcam and update the webcam label.
        """
        try:
            if self.cap is not None:
                # Read a frame from the webcam
                ret, frame = self.cap.read()

                # If we failed to capture a frame, print an error message and schedule the next frame update
                if not ret or frame is None:
                    print("Failed to capture frame from camera")
                    self.root.after(100, self.process_webcam)
                    return

                # Convert the frame to RGB (OpenCV uses BGR by default)
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert the image to a PhotoImage
                img_pil = Image.fromarray(img_rgb)

                # Create a PhotoImage from the image
                imgtk = ImageTk.PhotoImage(image=img_pil)

                # Update the webcam label with the new image
                self.webcam_label.imgtk = imgtk
                self.webcam_label.configure(image=imgtk)

                # Update the most recent frame with the current frame
                self.most_recent_capture_arr = frame

                # Schedule the next frame update
                self.root.after(20, self.process_webcam)
        except Exception as e:
            # If there's an error processing the webcam, print the error message
            print(f"Error processing webcam: {e}")

    def capture_and_save_new_image(self):
        """
        Capture the current frame from the webcam and save it as the user's new image.
        """
        if self.most_recent_capture_arr is None:
            util.msg_box("Error", "No image captured!")
            print("No image captured")
            return

        # Ensure there is exactly one face detected
        faces = self.detect_face(self.most_recent_capture_arr)
        if len(faces) != 1:
            util.msg_box("Error", "Exactly one face must be detected!")
            print("Exactly one face must be detected")
            return

        user_name = self.capture_user_name
        face_img_path = os.path.join(self.config.get('db_dir'), f"{user_name}.jpg")

        # Save the image as JPG
        cv2.imwrite(face_img_path, self.most_recent_capture_arr)
        print(f"Saved new face image to {face_img_path}")

        util.msg_box("Success", f"Image for {user_name} updated successfully!")

        # Close the capture window
        self.capture_image_window.destroy()

        # Release the camera
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def detect_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces


if __name__ == "__main__":
    root = ctk.CTk()
    app = ManageUsersApp(root)
    root.mainloop()