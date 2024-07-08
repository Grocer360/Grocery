# manage_users.py

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import psycopg2
from config import Config, get_db_connection
import util

class ManageUsersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Users")
        self.root.geometry("800x600")

        self.config = Config()

        self.tree = ttk.Treeview(root)
        self.tree["columns"] = ("User ID", "Username", "Logged In", "Time In", "Time Out", "Work Duration")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.heading("#0", text="", anchor=tk.CENTER)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, anchor=tk.CENTER, width=100)

        self.tree.pack(pady=20, fill=tk.BOTH, expand=True)
        self.refresh_button = util.get_button(self.root, 'Refresh Data', '#ff9800', self.load_data)

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = get_db_connection()
            if conn is None:
                util.msg_box("Error", "Cannot connect to the database.")
                return

            cursor = conn.cursor()

            cursor.execute("SELECT user_id, user_name, logged_in, time_stamp_in, time_stamp_out, work_duration FROM Users")
            rows = cursor.fetchall()

            for row in rows:
                formatted_row = (
                    row[0], 
                    row[1], 
                    'Yes' if row[2] else 'No',
                    util.format_datetime(row[3]),
                    util.format_datetime(row[4]),
                    f"{row[5]:.2f} hours" if row[5] else 'N/A'
                )
                self.tree.insert("", "end", values=formatted_row)

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error loading data: {e}")
            util.msg_box("Error", "Failed to load data. Please try again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ManageUsersApp(root)
    root.mainloop()
