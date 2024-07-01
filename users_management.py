import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
import bcrypt

def connect_db():
    return psycopg2.connect(
        dbname="grocery_database_system",
        user="anas",
        password="0000",
        host="localhost",
        port="5432"
    )

class UserManagementApp:
    def __init__(self, container):
        self.container = container

        # Frame to hold the user entry fields
        self.user_frame = ttk.Frame(self.container, padding="20")
        self.user_frame.grid(row=0, column=0, sticky="nsew")

        # User Details Entry Fields
        ttk.Label(self.user_frame, text="Username:").grid(row=0, column=0, sticky="w")
        self.username_entry = ttk.Entry(self.user_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.user_frame, text="Email:").grid(row=1, column=0, sticky="w")
        self.email_entry = ttk.Entry(self.user_frame, width=30)
        self.email_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.user_frame, text="Password:").grid(row=2, column=0, sticky="w")
        self.password_entry = ttk.Entry(self.user_frame, show='*', width=30)
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        # Buttons
        self.add_button = ttk.Button(self.user_frame, text="Add User", command=self.add_user)
        self.add_button.grid(row=3, column=0, padx=10, pady=10)

        self.delete_button = ttk.Button(self.user_frame, text="Delete User", command=self.delete_user)
        self.delete_button.grid(row=3, column=1, padx=10, pady=10)

        # Treeview to display users
        self.user_tree = ttk.Treeview(self.container, columns=("Username", "Email", "Role"), show="headings", height=10)
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Email", text="Email")
        self.user_tree.heading("Role", text="Role")
        self.user_tree.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        self.load_users()

    def load_users(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT username, email, role FROM users")
            users = cursor.fetchall()
            for user in users:
                self.user_tree.insert("", "end", values=user)
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def add_user(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        role = 'user'  # Default role

        if not username or not email or not password:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                           (username, email, hashed_password, role))
            conn.commit()
            cursor.close()
            conn.close()
            self.user_tree.insert("", "end", values=(username, email, role))
            self.clear_entries()
            messagebox.showinfo("Success", "User added successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_user(self):
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "No user selected.")
            return

        selected_user = self.user_tree.item(selected_item, "values")[0]

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (selected_user,))
            conn.commit()
            cursor.close()
            conn.close()
            self.user_tree.delete(selected_item)
            self.clear_entries()
            messagebox.showinfo("Success", "User deleted successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

# Integration with the admin page
def create_user_management_page(container):
    for widget in container.winfo_children():
        widget.destroy()
    UserManagementApp(container)




