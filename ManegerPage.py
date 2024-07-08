import sqlite3
import ctypes
from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import customtkinter as ctk
import logging
import csv
import hashlib


# Set CustomTkinter appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Initialize logging configuration
logging.basicConfig(filename='supermarket.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to execute SQL queries
def execute_query(query, params=()):
    conn = None
    try:
        conn = sqlite3.connect('DataBase.db')
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        log_error(e)
    finally:
        if conn:
            conn.close()

# Initialize database tables if they don't exist
def initialize_database():
    execute_query('''CREATE TABLE IF NOT EXISTS products (
                        barCode TEXT PRIMARY KEY,
                        prod_name TEXT NOT NULL,
                        price REAL NOT NULL,
                        quantity INTEGER NOT NULL)''')

    execute_query('''CREATE TABLE IF NOT EXISTS employees (
                        emp_id INTEGER PRIMARY KEY,
                        user_name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        working_hours REAL NOT NULL,
                        password TEXT NOT NULL)''')

# Function to add a new product to the database
# Improved error handling example in `add_product` function
def add_product(barCode, prod_name, price, quantity):
    if not validate_product_input(barCode, prod_name, price, quantity):
        return

    try:
        conn = sqlite3.connect('DataBase.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM products WHERE barCode=?", (barCode,))
        count = c.fetchone()[0]

        if count > 0:
            messagebox.showerror("Error", "Product with this barcode already exists.")
            return

        execute_query("INSERT INTO products (barCode, prod_name, price, quantity) VALUES (?, ?, ?, ?)",
                      (barCode, prod_name, price, quantity))
        log_action(f"Product added: {prod_name} ({barCode})")
        messagebox.showinfo("Success", "Product added successfully.")

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        log_error(e)

    finally:
        if conn:
            conn.close()

# Function to add a new employee to the database
def add_employee(emp_id, user_name, role, working_hours, password):
    if not validate_employee_input(emp_id, user_name, role, working_hours, password):
        return

    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hashing the password
    execute_query("INSERT INTO employees (emp_id, user_name, role, working_hours, password) VALUES (?, ?, ?, ?, ?)",
                  (emp_id, user_name, role, working_hours, hashed_password))
    log_action(f"Employee added: {user_name} ({emp_id})")
    messagebox.showinfo("Success", "Employee added successfully.")

# Function to validate product input fields
def validate_product_input(barCode, prod_name, price, quantity):
    try:
        barCode = float(barCode)
        price = float(price)
        quantity = int(quantity)
        if not barCode or not prod_name or price <= 0 or quantity < 0:
            raise ValueError("Invalid input values.")
    except ValueError:
        messagebox.showerror("Error", "Please fill in all fields with valid numeric data")
        return False
    return True


# Function to validate employee input fields
def validate_employee_input(emp_id, user_name, role, working_hours, password):
    try:
        emp_id = int(emp_id)
        working_hours = float(working_hours)
        if not emp_id or not user_name or not role or working_hours <= 0 or not password:
            raise ValueError("Invalid input values.")
    except ValueError:
        messagebox.showerror("Error", "Please fill in all fields with valid numeric data")
        return False
    return True

# Function to log actions
def log_action(action):
    logging.info(action)

def log_error(error):
    logging.error(error)


# Function to search products in the database based on a search term
def search_products(search_term):
    conn = sqlite3.connect('DataBase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE prod_name LIKE ?", ('%' + search_term + '%',))
    results = c.fetchall()
    conn.close()
    return results

# Function to export data to a CSV file
def export_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

# Function to delete a product from the database

def confirm_delete_product(barCode, product_name):
    response = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {product_name}?")
    if response:
        delete_product(barCode)

def delete_product(barCode):
    execute_query("DELETE FROM products WHERE barCode=?", (barCode,))
    log_action(f"Product deleted: {barCode}")
    messagebox.showinfo("Success", "Product deleted successfully.")

# Function to delete an employee from the database

def confirm_delete_employee(emp_id, user_name):
    response = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {user_name}?")
    if response:
        delete_product(emp_id)

def delete_employee(emp_id):
    execute_query("DELETE FROM employees WHERE emp_id=?", (emp_id,))
    log_action(f"Employee deleted: {emp_id}")
    messagebox.showinfo("Success", "Employee deleted successfully.")

# Function to update product details in the database
def update_product(barCode, prod_name, price, quantity):
    if not validate_product_input(barCode, prod_name, price, quantity):
        return

    execute_query("UPDATE products SET prod_name=?, price=?, quantity=? WHERE barCode=?",
                  (prod_name, price, quantity, barCode))
    log_action(f"Product updated: {prod_name} ({barCode})")
    messagebox.showinfo("Success", "Product updated successfully.")

# Function to update employee details in the database
def update_employee(emp_id, user_name, role, working_hours, password):
    if not validate_employee_input(emp_id, user_name, role, working_hours, password):
        return

    execute_query("UPDATE employees SET user_name=?, role=?, working_hours=?, password=? WHERE emp_id=?",
                  (user_name, role, working_hours, password, emp_id))
    log_action(f"Employee updated: {user_name} ({emp_id})")
    messagebox.showinfo("Success", "Employee updated successfully.")

# Main application class using CustomTkinter
class ManegerPage(ctk.CTk):
    def __init__(self, username):
        super().__init__()

        self.geometry('1280x720')
        self.after(10, self.fullscreen_and_disable_resize)
        self.title(f"Supermarket Management System - Welcome {username}")

        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.grid(row=0, column=1, sticky="ns", pady=0, padx=10)

        load_BGImg(self, 'adminBG.png', 'adminBG.png')

        self.btn_add_product = ctk.CTkButton(self.nav_frame, text="Add Product", command=self.show_add_product, width=150, height=70)
        self.btn_add_product.grid(row=0, column=0, padx=20, pady=(100,30))

        self.btn_add_employee = ctk.CTkButton(self.nav_frame, text="Add Employee", command=self.show_add_employee, width=150, height=70)
        self.btn_add_employee.grid(row=1, column=0, padx=20, pady=30)

        self.btn_view_products = ctk.CTkButton(self.nav_frame, text="View Products", command=self.show_view_products, width=150, height=70)
        self.btn_view_products.grid(row=2, column=0, padx=20, pady=30)

        self.btn_view_employees = ctk.CTkButton(self.nav_frame, text="View Employees", command=self.show_view_employees, width=150, height=70)
        self.btn_view_employees.grid(row=3, column=0, padx=20, pady=30)

        self.btn_search_product = ctk.CTkButton(self.nav_frame, text="Search Product", command=self.show_search_product, width=150, height=70)
        self.btn_search_product.grid(row=4, column=0, padx=20, pady=30)

        self.btn_logout = ctk.CTkButton(self.nav_frame, text="Logout", command=self.confirm_logout, fg_color="red")
        self.btn_logout.grid(row=5, column=0, padx=20, pady=50)

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=2, sticky="nw", pady=90, padx=10)

        self.show_add_product()

    # Function to enable fullscreen mode and disable resizing
    def fullscreen_and_disable_resize(self):
        self.overrideredirect(True)
        self.state('zoomed')
        self.bind("<Escape>", self.exit_fullscreen)

    # Function to exit fullscreen mode
    def exit_fullscreen(self, event=None):
        self.overrideredirect(False)
        self.state('normal')
        self.after(4000, self.fullscreen_and_disable_resize)
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        user32.ShowWindow(hwnd, 3)
        style = user32.GetWindowLongW(hwnd, -16)
        style &= ~0x00040000
        style &= ~0x00010000
        user32.SetWindowLongW(hwnd, -16, style)

    # Function to display the add product form
    def show_add_product(self):
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="Add New Product", font=("Arial", 24)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        ctk.CTkLabel(self.content_frame, text="Barcode:").grid(row=1, column=0, sticky="e", padx=20, pady=5)
        barCode_entry = ctk.CTkEntry(self.content_frame)
        barCode_entry.grid(row=1, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Product Name:").grid(row=2, column=0, sticky="e", padx=20, pady=5)
        prod_name_entry = ctk.CTkEntry(self.content_frame)
        prod_name_entry.grid(row=2, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Price:").grid(row=3, column=0, sticky="e", padx=20, pady=5)
        price_entry = ctk.CTkEntry(self.content_frame)
        price_entry.grid(row=3, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Quantity:").grid(row=4, column=0, sticky="e", padx=20, pady=5)
        quantity_entry = ctk.CTkEntry(self.content_frame)
        quantity_entry.grid(row=4, column=1, padx=20, pady=5)

        def submit():
            try:
                barCode = barCode_entry.get()
                prod_name = prod_name_entry.get()
                price = float(price_entry.get())
                quantity = int(quantity_entry.get())
                add_product(barCode, prod_name, price, quantity)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for Price and Quantity")

        ctk.CTkButton(self.content_frame, text="Add Product", command=submit).grid(row=5, column=0, columnspan=2, padx=20, pady=20)

    # Function to display the add employee form
    def show_add_employee(self):
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="Add New Employee", font=("Arial", 24)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        ctk.CTkLabel(self.content_frame, text="Employee ID:").grid(row=1, column=0, sticky="e", padx=20, pady=5)
        emp_id_entry = ctk.CTkEntry(self.content_frame)
        emp_id_entry.grid(row=1, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="User Name:").grid(row=2, column=0, sticky="e", padx=20, pady=5)
        user_name_entry = ctk.CTkEntry(self.content_frame)
        user_name_entry.grid(row=2, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Role:").grid(row=3, column=0, sticky="e", padx=20, pady=5)
        role_entry = ctk.CTkEntry(self.content_frame)
        role_entry.grid(row=3, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Working Hours:").grid(row=4, column=0, sticky="e", padx=20, pady=5)
        working_hours_entry = ctk.CTkEntry(self.content_frame)
        working_hours_entry.grid(row=4, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Password:").grid(row=5, column=0, sticky="e", padx=20, pady=5)
        password_entry = ctk.CTkEntry(self.content_frame, show="*")
        password_entry.grid(row=5, column=1, padx=20, pady=5)

        def submit():
            try:
                emp_id = int(emp_id_entry.get())
                user_name = user_name_entry.get()
                role = role_entry.get()
                working_hours = float(working_hours_entry.get())
                password = password_entry.get()
                add_employee(emp_id, user_name, role, working_hours, password)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for Employee ID and Working Hours")

        ctk.CTkButton(self.content_frame, text="Add Employee", command=submit).grid(row=6, column=0, columnspan=2, padx=20, pady=20)

    # Function to display the products list
    def show_view_products(self):
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="Products List", font=("Arial", 24)).grid(row=0, column=0, padx=20, pady=20)

        treeview = ttk.Treeview(self.content_frame, columns=("Barcode", "Name", "Price", "Quantity"), show="headings")
        treeview.heading("Barcode", text="Barcode")
        treeview.heading("Name", text="Name")
        treeview.heading("Price", text="Price")
        treeview.heading("Quantity", text="Quantity")

        treeview.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        conn = sqlite3.connect('DataBase.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        products = c.fetchall()
        conn.close()

        for product in products:
            treeview.insert("", "end", values=product)

        def export():
            export_to_csv(products, "products.csv")
            messagebox.showinfo("Success", "Products exported successfully.")

        def delete():
            selected_item = treeview.selection()
            if selected_item:
                item = treeview.item(selected_item)['values']
                confirm_delete_product(item[0], item[1])
                treeview.delete(selected_item)
            else:
                messagebox.showwarning("Delete Error", "Please select a product to delete.")

        def modify():
            selected_item = treeview.selection()
            if selected_item:
                item = treeview.item(selected_item)['values']
                modify_product_window(item)                
            else:
                messagebox.showwarning("Modify Error", "Please select a product to modify.")

        ctk.CTkButton(self.content_frame, text="Modify Product", command=modify).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(self.content_frame, text="Delete Product", command=delete, fg_color="red").grid(row=4, column=0, padx=20, pady=10)
        ctk.CTkButton(self.content_frame, text="Export to CSV", command=export).grid(row=5, column=0, padx=20, pady=10)

                
    # Function to display the employees list
    def show_view_employees(self):
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="Employees List", font=("Arial", 24)).grid(row=0, column=0, padx=20, pady=20)

        treeview = ttk.Treeview(self.content_frame, columns=("ID", "User Name", "Role", "Working Hours"), show="headings")
        treeview.heading("ID", text="ID")
        treeview.heading("User Name", text="User Name")
        treeview.heading("Role", text="Role")
        treeview.heading("Working Hours", text="Working Hours")

        treeview.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        conn = sqlite3.connect('DataBase.db')
        c = conn.cursor()
        c.execute("SELECT * FROM employees")
        employees = c.fetchall()
        conn.close()

        for employee in employees:
            treeview.insert("", "end", values=employee)

        def export():
            export_to_csv(employees, "employees.csv")
            messagebox.showinfo("Success", "Employees exported successfully.")

        def delete():
            selected_item = treeview.selection()
            if selected_item:
                item = treeview.item(selected_item)['values']
                confirm_delete_employee(item[0], item[1])
                treeview.delete(selected_item)
            else:
                messagebox.showwarning("Delete Error", "Please select an employee to delete.")

        def modify():
            selected_item = treeview.selection()
            if selected_item:
                item = treeview.item(selected_item)['values']
                modify_employee_window(item)
            else:
                messagebox.showwarning("Modify Error", "Please select an employee to modify.")


        ctk.CTkButton(self.content_frame, text="Delete Employee", command=delete, fg_color='red').grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.content_frame, text="Modify Employee", command=modify).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(self.content_frame, text="Export to CSV", command=export).grid(row=4, column=0, padx=20, pady=10)

    # Function to display the search product interface
    def show_search_product(self):
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="Search Product", font=("Arial", 24)).grid(row=0, column=0, padx=20, pady=20)

        search_entry = ctk.CTkEntry(self.content_frame)
        search_entry.grid(row=1, column=0, padx=20, pady=5)

        def search():
            search_term = search_entry.get()
            results = search_products(search_term)
            for item in treeview.get_children():
                treeview.delete(item)
            for product in results:
                treeview.insert("", "end", values=product)

        treeview = ttk.Treeview(self.content_frame, columns=("Barcode", "Name", "Price", "Quantity"), show="headings")
        treeview.heading("Barcode", text="Barcode")
        treeview.heading("Name", text="Name")
        treeview.heading("Price", text="Price")
        treeview.heading("Quantity", text="Quantity")
        treeview.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkButton(self.content_frame, text="Search", command=search).grid(row=1, column=1, padx=20, pady=5)

    # Function to clear the content frame
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # Function to confirm logout
    def confirm_logout(self):
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            self.destroy()

# Function to modify product details
def modify_product_window(item):
    modify_window = Toplevel()
    modify_window.title("Modify Product")
    modify_window.geometry("400x300")

    ctk.CTkLabel(modify_window, text="Product Name:").grid(row=0, column=0, padx=20, pady=10)
    prod_name_entry = ctk.CTkEntry(modify_window)
    prod_name_entry.grid(row=0, column=1, padx=20, pady=10)
    prod_name_entry.insert(0, item[1])

    ctk.CTkLabel(modify_window, text="Price:").grid(row=1, column=0, padx=20, pady=10)
    price_entry = ctk.CTkEntry(modify_window)
    price_entry.grid(row=1, column=1, padx=20, pady=10)
    price_entry.insert(0, item[2])

    ctk.CTkLabel(modify_window, text="Quantity:").grid(row=2, column=0, padx=20, pady=10)
    quantity_entry = ctk.CTkEntry(modify_window)
    quantity_entry.grid(row=2, column=1, padx=20, pady=10)
    quantity_entry.insert(0, item[3])

    def submit():
        prod_name = prod_name_entry.get()
        price = float(price_entry.get())
        quantity = int(quantity_entry.get())
        update_product(item[0], prod_name, price, quantity)
        modify_window.destroy()

    ctk.CTkButton(modify_window, text="Update", command=submit).grid(row=3, column=0, columnspan=2, padx=20, pady=20)

# Function to modify employee details
def modify_employee_window(item):
    modify_window = Toplevel()
    modify_window.title("Modify Employee")
    modify_window.geometry("400x300")

    ctk.CTkLabel(modify_window, text="User Name:").grid(row=0, column=0, padx=20, pady=10)
    user_name_entry = ctk.CTkEntry(modify_window)
    user_name_entry.grid(row=0, column=1, padx=20, pady=10)
    user_name_entry.insert(0, item[1])

    ctk.CTkLabel(modify_window, text="Role:").grid(row=1, column=0, padx=20, pady=10)
    role_entry = ctk.CTkEntry(modify_window)
    role_entry.grid(row=1, column=1, padx=20, pady=10)
    role_entry.insert(0, item[2])

    ctk.CTkLabel(modify_window, text="Working Hours:").grid(row=2, column=0, padx=20, pady=10)
    working_hours_entry = ctk.CTkEntry(modify_window)
    working_hours_entry.grid(row=2, column=1, padx=20, pady=10)
    working_hours_entry.insert(0, item[3])

    ctk.CTkLabel(modify_window, text="Password:").grid(row=3, column=0, padx=20, pady=10)
    password_entry = ctk.CTkEntry(modify_window, show="*")
    password_entry.grid(row=3, column=1, padx=20, pady=10)
    password_entry.insert(0, item[4])

    def submit():
        user_name = user_name_entry.get()
        role = role_entry.get()
        working_hours = float(working_hours_entry.get())
        password = password_entry.get()
        update_employee(item[0], user_name, role, working_hours, password)
        modify_window.destroy()

    ctk.CTkButton(modify_window, text="Update", command=submit).grid(row=4, column=0, columnspan=2, padx=20, pady=20)

def load_BGImg(app, light_image_path, dark_image_path):
    try:
        light_image = Image.open(light_image_path).resize((400, 850))
        dark_image = Image.open(dark_image_path).resize((400, 850))
        my_image = ctk.CTkImage(light_image=light_image, dark_image=dark_image, size=(400, 870))
        image_label = ctk.CTkLabel(app, image=my_image, text="")
        image_label.grid(row=0, column=0, sticky="nsew")
    except IOError as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")


# Main function to run the application
def main():
    initialize_database()
    app = ManegerPage('username')
    app.mainloop()

if __name__ == "__main__":
    main()



'''
# Example of sending notification for low stock
def check_stock_levels():
    cursor.execute("SELECT * FROM products WHERE stock_quantity < 10")
    low_stock_products = cursor.fetchall()
    
    if low_stock_products:
        send_notification("Low Stock Alert", f"The following products are running low on stock: {', '.join([product['name'] for product in low_stock_products])}")
'''