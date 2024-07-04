import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk  # Assuming customtkinter is a custom library you've defined
import psycopg2
from datetime import datetime

# Database connection
try:
    db = psycopg2.connect(
        dbname="barcode",
        user="abdelrahman",
        password="1997",
        host="localhost",
        port="5432"
    )
    cursor = db.cursor()
except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")
    exit(1)

# GUI application
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Grocery Store System")
        self.geometry("800x600")

        # User login frame
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=20)

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username")
        self.username_entry.pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=5)
        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        # Admin frame
        self.admin_frame = ctk.CTkFrame(self)
        self.admin_frame.pack_forget()

        self.products_listbox = tk.Listbox(self.admin_frame, width=50, height=20)
        self.products_listbox.pack(pady=10)

        self.add_product_button = ctk.CTkButton(self.admin_frame, text="Add Product", command=self.add_product)
        self.add_product_button.pack(pady=10)
        self.edit_product_button = ctk.CTkButton(self.admin_frame, text="Edit Product", command=self.edit_product)
        self.edit_product_button.pack(pady=10)
        self.delete_product_button = ctk.CTkButton(self.admin_frame, text="Delete Product", command=self.delete_product)
        self.delete_product_button.pack(pady=10)
        self.sell_product_button = ctk.CTkButton(self.admin_frame, text="Sell Product", command=self.sell_product)
        self.sell_product_button.pack(pady=10)
        self.logout_button = ctk.CTkButton(self.admin_frame, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)

        self.logged_in_user = None

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            cursor.execute("SELECT * FROM Users WHERE user_name=%s AND password=%s", (username, password))
            user = cursor.fetchone()

            if user:
                self.logged_in_user = user
                self.login_frame.pack_forget()
                self.admin_frame.pack(pady=20)
                self.update_login_status(True)
                self.load_products()  # Load products after successful login
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Error during login: {e}")

    def logout(self):
        self.logged_in_user = None
        self.admin_frame.pack_forget()
        self.login_frame.pack(pady=20)
        self.update_login_status(False)

    def update_login_status(self, logged_in):
        if self.logged_in_user:
            try:
                cursor.execute("UPDATE Users SET logged_in=%s WHERE user_id=%s", (logged_in, self.logged_in_user[0]))
                db.commit()
            except psycopg2.Error as e:
                messagebox.showerror("Database Error", f"Error updating login status: {e}")

    def load_products(self):
        self.products_listbox.delete(0, tk.END)  # Clear previous items
        try:
            cursor.execute("SELECT barCode, prod_name, quantity, category, price FROM Products")
            products = cursor.fetchall()
            for product in products:
                self.products_listbox.insert(tk.END, f"{product[0]} - {product[1]} - {product[2]} - {product[3]} - {product[4]}")
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Error fetching products: {e}")

    def add_product(self):
        self.product_window("Add Product", self.save_new_product)

    def edit_product(self):
        self.product_window("Edit Product", self.save_edited_product)

    def delete_product(self):
        barcode = self.get_product_barcode()
        if barcode:
            try:
                cursor.execute("DELETE FROM Products WHERE barCode=%s", (barcode,))
                db.commit()
                messagebox.showinfo("Success", "Product deleted successfully")
                self.load_products()  # Reload products after deletion
            except psycopg2.Error as e:
                messagebox.showerror("Database Error", f"Error deleting product: {e}")

    def sell_product(self):
        barcode = self.get_product_barcode()
        if barcode:
            quantity = self.get_product_quantity()
            try:
                cursor.execute("INSERT INTO Interactions (barcode, user_id, time_stamp) VALUES (%s, %s, %s)", (barcode, self.logged_in_user[0], datetime.now()))
                cursor.execute("UPDATE Products SET quantity=quantity-%s WHERE barCode=%s", (quantity, barcode))
                db.commit()
                messagebox.showinfo("Success", "Product sold successfully")
                self.load_products()  # Reload products after selling
            except psycopg2.Error as e:
                messagebox.showerror("Database Error", f"Error selling product: {e}")

    def product_window(self, title, save_command):
        window = ctk.CTkToplevel(self)
        window.title(title)

        self.prod_barcode_entry = ctk.CTkEntry(window, placeholder_text="Barcode")
        self.prod_barcode_entry.pack(pady=5)
        self.prod_name_entry = ctk.CTkEntry(window, placeholder_text="Product Name")
        self.prod_name_entry.pack(pady=5)
        self.prod_quantity_entry = ctk.CTkEntry(window, placeholder_text="Quantity")
        self.prod_quantity_entry.pack(pady=5)
        self.prod_category_entry = ctk.CTkEntry(window, placeholder_text="Category")
        self.prod_category_entry.pack(pady=5)
        self.prod_price_entry = ctk.CTkEntry(window, placeholder_text="Price")
        self.prod_price_entry.pack(pady=5)
        save_button = ctk.CTkButton(window, text="Save", command=lambda: save_command(window))
        save_button.pack(pady=10)

    def save_new_product(self, window):
        barcode = self.prod_barcode_entry.get()
        name = self.prod_name_entry.get()
        quantity = self.prod_quantity_entry.get()
        category = self.prod_category_entry.get()
        price = self.prod_price_entry.get()

        try:
            cursor.execute("INSERT INTO Products (barCode, prod_name, quantity, category, price) VALUES (%s, %s, %s, %s, %s)",
                           (barcode, name, quantity, category, price))
            db.commit()
            messagebox.showinfo("Success", "Product added successfully")
            window.destroy()  # Close the product window after successful operation
            self.load_products()  # Reload products after adding
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Error adding product: {e}")

    def save_edited_product(self, window):
        barcode = self.prod_barcode_entry.get()
        name = self.prod_name_entry.get()
        quantity = self.prod_quantity_entry.get()
        category = self.prod_category_entry.get()
        price = self.prod_price_entry.get()

        try:
            cursor.execute("UPDATE Products SET prod_name=%s, quantity=%s, category=%s, price=%s WHERE barCode=%s",
                           (name, quantity, category, price, barcode))
            db.commit()
            messagebox.showinfo("Success", "Product updated successfully")
            window.destroy()  # Close the product window after successful operation
            self.load_products()  # Reload products after updating
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"Error updating product: {e}")

    def get_product_barcode(self):
        return self.ask_for_input("Enter product barcode:")

    def get_product_quantity(self):
        return self.ask_for_input("Enter quantity sold:")

    def ask_for_input(self, prompt):
        return simpledialog.askstring("Input", prompt, parent=self)

if __name__ == "__main__":
    app = App()
    app.mainloop()

# Close database connection when the application exits
try:
    cursor.close()
    db.close()
except psycopg2.Error as e:
    print(f"Error closing database connection: {e}")
