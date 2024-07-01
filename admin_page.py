import tkinter as tk
from tkinter import ttk
from product_management import ProductManagementApp
from add_product_to_cart import CartManagementApp
from users_management import UserManagementApp

class AdminPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Page")

        self.create_admin_interface()
        self.show_page("Product Management")  # Set the default page to Product Management

    def create_admin_interface(self):
        self.left_frame = ttk.Frame(self.root, width=200, height=600, padding="10")
        self.left_frame.grid(row=0, column=0, sticky="nswe")
        self.right_frame = ttk.Frame(self.root, width=400, height=600, padding="10")
        self.right_frame.grid(row=0, column=1, sticky="nswe")

        # Left frame buttons
        self.buttons = [
            "Product Management",
            "Sales Processing",
            "Reporting and Analytics",
            "User Management",
            "Settings"
        ]

        for i, btn_text in enumerate(self.buttons):
            button = ttk.Button(self.left_frame, text=btn_text, command=lambda text=btn_text: self.show_page(text))
            button.pack(fill='x', pady=5)

    def show_page(self, page):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        if page == "Product Management":
            ProductManagementApp(self.right_frame)
            
        elif page == "Sales Processing":
            CartManagementApp(self.right_frame)
            
        # Add other conditions here for different pages
        # elif page == "Reporting and Analytics":
        #     ReportingAnalyticsApp(self.right_frame)
        
        elif page == "User Management":
            UserManagementApp(self.right_frame)
        
        # elif page == "Settings":
        #     SettingsApp(self.right_frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminPage(root)
    root.mainloop()


