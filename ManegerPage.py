import psycopg2
from psycopg2 import sql
from psycopg2 import OperationalError
import ctypes
from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import customtkinter as ctk
import logging
import csv
import hashlib
from data_visualisation  import DataVisualisation
from scrollable_frame import ScrollableFrame 
from register import RegisterUserApp
from manage import ManageUsersApp





# Initialize logging configuration
logging.basicConfig(filename='supermarket.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
# Live Database Info
conn_details = {
    "dbname": "okzegkwz", 
    "user": "okzegkwz",
    "password": "7UwFflnPy3byudSr32K1ugHniRSVK6v_",
    "host": "kandula.db.elephantsql.com",
    "port": "5432"
}

# Set CustomTkinter appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def execute_query(query, params=()):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="okzegkwz",
            user="okzegkwz",
            password="7UwFflnPy3byudSr32K1ugHniRSVK6v_",
            host="kandula.db.elephantsql.com",
            port="5432"
        )
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
    except OperationalError as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        log_error(e)
    finally:
        if conn:
            conn.close()

# Function to add product 
def add_product(barCode, prod_name, price, quantity,category):
    if not validate_product_input(barCode, prod_name, price, quantity,category):
        return

    try:
        # Check if the product already exists
        query = "SELECT COUNT(*) FROM products WHERE bar_code=%s"
        params = (barCode,)
        count_cursor = execute_query(query, params)

        if count_cursor:
            count = count_cursor.fetchone()[0]

            if count > 0:
                messagebox.showerror("Error", "Product with this barcode already exists.")
                return

        # Insert the product if it doesn't exist
        query = "INSERT INTO products (bar_code, prod_name,quantity, category,price) VALUES (%s, %s, %s, %s,%s)"
        params = (barCode, prod_name,quantity,category,price)
        execute_query(query, params)
        log_action(f"Product added: {prod_name} ({barCode})")
        messagebox.showinfo("Success", "Product added successfully.")

    except OperationalError as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        log_error(e)
        
# Function to validate product input fields
def validate_product_input(barCode, prod_name, price, quantity,category):
    try:
        barCode = (barCode)
        price = int(price)
        quantity = int(quantity)
        category = category
        if not barCode or not prod_name or price <= 0 or quantity < 0:
            raise ValueError("Invalid input values.")
    except ValueError:
        messagebox.showerror("Error", "Please fill in all fields with valid numeric data")
        return False
    return True

# window Function to modify product details
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
    quantity_entry.insert(0, item[4])
    
    
    ctk.CTkLabel(modify_window, text="Category:").grid(row=3, column=0, padx=20, pady=10)
    category_entry = ctk.CTkEntry(modify_window)
    category_entry.grid(row=3, column=1, padx=20, pady=10)
    category_entry.insert(0, item[3])

    def submit():
        prod_name = prod_name_entry.get()
        price = float(price_entry.get())
        quantity = float(quantity_entry.get())
        category = category_entry.get()
        update_product(str(item[0]), prod_name, price, quantity,category)
        modify_window.destroy()

    ctk.CTkButton(modify_window, text="Update", command=submit).grid(row=4, column=0, columnspan=2, padx=20, pady=20)

#new
def search_product(bar_code):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="okzegkwz",
            user="okzegkwz",
            password="7UwFflnPy3byudSr32K1ugHniRSVK6v_",
            host="kandula.db.elephantsql.com",
            port="5432"
        )
        c = conn.cursor()
        # c.execute("SELECT * FROM products WHERE bar_code = %s", (bar_code))
        c.execute("SELECT * FROM products WHERE bar_code ILIKE %s", ('%' + bar_code + '%',))
        results = c.fetchall()

        if results:
            result_str = "\n".join([f"Barcode: {row[0]}\n Name: {row[1]}\n Quantity: {row[2]}\n Category: {row[3]}\n Price: {row[4]}\n" for row in results])
            messagebox.showinfo("Search Results", result_str)
        else:
            messagebox.showinfo("Search Results", "No product found with that name.")
    except OperationalError as e:
        messagebox.showerror("Database Error", f"Error during database operation: {e}")
    finally:
        if conn:
            conn.close()

def search_product_window():
    search_window = Toplevel()
    search_window.title("Modify Product")
    search_window.geometry("400x300")

    ctk.CTkLabel(search_window, text="Enter barcode").grid(row=0, column=0, padx=20, pady=10)
    bar_code_entry = ctk.CTkEntry(search_window)
    bar_code_entry.grid(row=0, column=1, padx=20, pady=10)
   

    def submit():
        bar_code = str(bar_code_entry.get())
        search_product(bar_code)
       
        search_window.destroy()

    ctk.CTkButton(search_window, text="Search", command=submit).grid(row=4, column=0, columnspan=2, padx=20, pady=20)

# Function to delete product 
def delete_product(barCode):
    try:
        execute_query("DELETE FROM products WHERE bar_code=%s", (barCode,))
        log_action(f"Product deleted: {barCode}")
        messagebox.showinfo("Success", "Product deleted successfully.")
    except OperationalError as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        log_error(e)
# Function to delete a product from the database
def confirm_delete_product(barCode, product_name):
    response = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {product_name}?")
    if response:
        delete_product(barCode)
# Function to update product details

def update_product(barCode, prod_name, price, quantity,category):
    if not validate_product_input(barCode, prod_name, price, quantity,category):
        return

    try:
        execute_query("UPDATE products SET prod_name=%s, price=%s, quantity=%s,category=%s WHERE bar_code=%s",
                      (prod_name, price, quantity, category,barCode))
        log_action(f"Product updated: {prod_name} ({barCode})")
        messagebox.showinfo("Success", "Product updated successfully.")
    except OperationalError as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        log_error(e)


#-------------------------------------------------------------------------------------------------------------

# Function to add employee 
def add_employee( user_name, role, working_hours, password):
    if not validate_employee_input( user_name, role, working_hours, password):
        return

    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hashing the password
    execute_query("INSERT INTO users ( user_name, role,working_hours, password) VALUES (%s, %s, %s, %s)",
                  ( user_name, role, working_hours, hashed_password))
    log_action(f"Employee added: {user_name}")
    messagebox.showinfo("Success", "Employee added successfully.")

# Function to validate employee input fields
def validate_employee_input(user_name, role, working_hours, password):
    try:
        # emp_id = int(emp_id)
        working_hours = (working_hours)
        if  not user_name or not role  or not password:
            raise ValueError("Invalid input values.")
    except ValueError:
        messagebox.showerror("Error", "Please fill in all fields with valid numeric data")
        return False
    return True
# Function to modify employee details
def modify_employee_window(item):
    modify_window = Toplevel()
    modify_window.title("Modify Employee")
    modify_window.geometry("400x300")

    ctk.CTkLabel(modify_window, text="User Name:").grid(row=0, column=0, padx=20, pady=10)
    user_name_entry = ctk.CTkEntry(modify_window)
    user_name_entry.grid(row=0, column=1, padx=20, pady=10)
    user_name_entry.insert(0, item[0])

    ctk.CTkLabel(modify_window, text="Role:").grid(row=1, column=0, padx=20, pady=10)
    role_entry = ctk.CTkEntry(modify_window)
    role_entry.grid(row=1, column=1, padx=20, pady=10)
    role_entry.insert(0, item[1])

    ctk.CTkLabel(modify_window, text="Working Hours:").grid(row=2, column=0, padx=20, pady=10)
    working_hours_entry = ctk.CTkEntry(modify_window)
    working_hours_entry.grid(row=2, column=1, padx=20, pady=10)
    working_hours_entry.insert(0, item[2])

    ctk.CTkLabel(modify_window, text="Password:").grid(row=3, column=0, padx=20, pady=10)
    password_entry = ctk.CTkEntry(modify_window, show="*")
    password_entry.grid(row=3, column=1, padx=20, pady=10)
    password_entry.insert(0, item[2])

    def submit():
        user_name = user_name_entry.get()
        role = role_entry.get()
        working_hours = (working_hours_entry.get())
        password = password_entry.get()
        update_employee(item[0],user_name, role, working_hours, password)
        modify_window.destroy()

   
    ctk.CTkButton(modify_window, text="Update", command=submit).grid(row=4, column=0, columnspan=2, padx=20, pady=20)
    
def update_employee( original_user_name,user_name, role, working_hours, password,):
    if not validate_employee_input( user_name, role, working_hours, password):
        return

    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hashing the password

    try:
        execute_query("UPDATE users SET user_name=%s, role=%s, working_hours=%s, password=%s WHERE user_name=%s",
                      (user_name, role, working_hours, hashed_password,original_user_name))
        log_action(f"Employee updated: {user_name}")
        messagebox.showinfo("Success", "Employee updated successfully.")
    except OperationalError as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        log_error(e)

        
# Function to log actions
def delete_employee(emp_id):
    try:
        execute_query("DELETE FROM users WHERE  user_name=%s", (emp_id,))
        log_action(f"Employee deleted: {emp_id}")
        messagebox.showinfo("Success", "Employee deleted successfully.")
    except OperationalError as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        log_error(e)
def confirm_delete_employee(emp_id, user_name):
    response = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {user_name}?")
    if response:
        delete_employee(emp_id)

def log_action(action):
    logging.info(action)

def log_error(error):
    logging.error(error)

# Function to export data to a CSV file
def export_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

# Main application class using CustomTkinter
class ManegerPage(ctk.CTk):
    def __init__(self, username):
        super().__init__()

        self.geometry('1280x720')
        self.after(10, self.fullscreen_and_disable_resize)
        self.title(f"Supermarket Management System - Welcome {username}")
        self.tkraise()

        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.grid(row=0, column=1, sticky="nw", pady=90, padx=20)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.content_frame = ScrollableFrame(self)
        self.content_frame.grid(row=0, column=2, sticky="nsew", padx=20, pady=90)

        load_BGImg(self, './assets/AdminBG.png')

        self.btn_add_product = ctk.CTkButton(self.nav_frame, text="Add Product", command=self.show_add_product, width=150, height=50)
        self.btn_add_product.grid(row=0, column=0, padx=20, pady=20)

        self.btn_add_employee = ctk.CTkButton(self.nav_frame, text="Register Users", command=self.show_add_employee, width=150, height=50)
        self.btn_add_employee.grid(row=1, column=0, padx=20, pady=20)

        self.btn_view_products = ctk.CTkButton(self.nav_frame, text="View Products", command=self.show_view_products, width=150, height=50)
        self.btn_view_products.grid(row=2, column=0, padx=20, pady=20)

        self.btn_view_employees = ctk.CTkButton(self.nav_frame, text="Mnage Users", command=self.show_view_employees, width=150, height=50)
        self.btn_view_employees.grid(row=3, column=0, padx=20, pady=20)

        # self.btn_search_product = ctk.CTkButton(self.nav_frame, text="Search Product", command=self.show_search_product, width=150, height=50)
        # self.btn_search_product.grid(row=4, column=0, padx=20, pady=20)
        
        self.btn_data_and_statistics = ctk.CTkButton(self.nav_frame, text="Data and Statistics", command=self.initialize_data_visualisation, width=150, height=50)
        self.btn_data_and_statistics.grid(row=4, column=0, padx=20, pady=20)

        self.btn_logout = ctk.CTkButton(self.nav_frame, text="Return to Login", command=self.confirm_logout, fg_color="Black")
        self.btn_logout.grid(row=5, column=0, padx=20, pady=20)
        

        self.initialize_data_visualisation()

        
    def initialize_data_visualisation(self):
        # Clear the content frame
        self.clear_content_frame()

        # Initialize the DataVisualisation class and pack it into the content_frame
        self.data_visualisation = DataVisualisation(self.content_frame.scrollable_frame)
        self.data_visualisation.grid(row=0, column=0, sticky="nsew")

        self.content_frame.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.scrollable_frame.grid_columnconfigure(0, weight=1)


    # Function to enable fullscreen mode and disable resizing
    def fullscreen_and_disable_resize(self):
        self.overrideredirect(False)
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
        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Add New Product", font=("Arial", 24)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Barcode:").grid(row=1, column=0, sticky="e", padx=20, pady=5)
        barCode_entry = ctk.CTkEntry(self.content_frame.scrollable_frame)
        barCode_entry.grid(row=1, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Product Name:").grid(row=2, column=0, sticky="e", padx=20, pady=5)
        prod_name_entry = ctk.CTkEntry(self.content_frame.scrollable_frame)
        prod_name_entry.grid(row=2, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Price:").grid(row=3, column=0, sticky="e", padx=20, pady=5)
        price_entry = ctk.CTkEntry(self.content_frame.scrollable_frame)
        price_entry.grid(row=3, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Quantity:").grid(row=4, column=0, sticky="e", padx=20, pady=5)
        quantity_entry = ctk.CTkEntry(self.content_frame.scrollable_frame)
        quantity_entry.grid(row=4, column=1, padx=20, pady=5)
        
        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Category:").grid(row=5, column=0, sticky="e", padx=20, pady=5)
        category_entry = ctk.CTkEntry(self.content_frame.scrollable_frame)
        category_entry.grid(row=5, column=1, padx=20, pady=5)

        def submit():
            try:
                barCode = barCode_entry.get()
                prod_name = prod_name_entry.get()
                price = int(price_entry.get())
                quantity = int(quantity_entry.get())
                category = category_entry.get()
                add_product(barCode, prod_name, price, quantity,category)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for Price and Quantity")

        ctk.CTkButton(self.content_frame.scrollable_frame, text="Add Product", command=submit).grid(row=6, column=0, columnspan=2, padx=20, pady=20)

    # Function to display the add employee form
    def show_add_employee(self):
        try:
            print("Sign Up with Face clicked")
            register_window = ctk.CTkToplevel()  # Create a new top-level window using ctk.CTkToplevel
            app = RegisterUserApp(register_window)  # Create an instance of RegisterUserApp
            register_window.mainloop()  # Start the main loop for the registration window
        except Exception as e:
            print(f"Error during sign up with face: {e}")
        
        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Add New Employee", font=("Arial", 24)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
    

        ctk.CTkLabel(self.content_frame.scrollable_frame, text="User Name:").grid(row=2, column=0, sticky="e", padx=20, pady=5)
        user_name_entry = ctk.CTkEntry(self.content_frame.scrollable_frame)
        user_name_entry.grid(row=2, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Role:").grid(row=3, column=0, sticky="e", padx=20, pady=5)
        role_entry = ctk.CTkEntry(self.content_frame.scrollable_frame)
        role_entry.grid(row=3, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Working Hours:").grid(row=4, column=0, sticky="e", padx=20, pady=5)
        working_hours_entry = ctk.CTkEntry(self.content_frame.scrollable_frame)
        working_hours_entry.grid(row=4, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame.scrollable_frame, text="Password:").grid(row=5, column=0, sticky="e", padx=20, pady=5)
        password_entry = ctk.CTkEntry(self.content_frame.scrollable_frame, show="*")
        password_entry.grid(row=5, column=1, padx=20, pady=5)

        def submit():
            try:
                # emp_id = int(emp_id_entry.get())
                user_name = user_name_entry.get()
                role = role_entry.get()
                working_hours = (working_hours_entry.get())
                password = password_entry.get()
                add_employee( user_name, role, working_hours, password)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for Employee ID and Working Hours")

        ctk.CTkButton(self.content_frame.scrollable_frame, text="Add Employee", command=submit).grid(row=6, column=0, columnspan=2, padx=20, pady=20)

    # Function to display the products list
    def show_view_products(self):
        self.clear_content_frame()

        try:
           
            conn = psycopg2.connect(
                dbname="okzegkwz",
                user="okzegkwz",
                password="7UwFflnPy3byudSr32K1ugHniRSVK6v_",
                host="kandula.db.elephantsql.com",
                port="5432"
            )

            query = "SELECT * FROM products"
            c = conn.cursor()
            c.execute(query)
            products = c.fetchall()
            conn.close()

            ctk.CTkLabel(self.content_frame.scrollable_frame, text="Products List", font=("Arial", 24)).grid(row=0, column=0, padx=20, pady=20)

            style = ttk.Style()
            style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))  # Adjust the font size and style as needed
            style.configure("Treeview", font=("Helvetica", 12))  # Adjust the font size as needed

            treeview = ttk.Treeview(self.content_frame.scrollable_frame,columns=("Barcode", "Name" ,"Price","Category","Quantity"), show="headings")
            treeview.column("Barcode", width=200, anchor='center')  # Adjust the width as needed
            treeview.column("Name", width=200, anchor='center')     # Adjust the width as needed
            treeview.column("Price", width=200, anchor='center')    # Adjust the width as needed
            treeview.column("Category", width=200, anchor='center')
            treeview.heading("Barcode", text="Barcode", anchor='center')
            treeview.heading("Name", text="Name", anchor='center')
            treeview.heading("Price", text="Price", anchor='center')
            treeview.heading("Quantity", text="Quantity", anchor='center')
            treeview.heading("Category", text="Category", anchor='center')

            treeview.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
            self.content_frame.scrollable_frame.grid_rowconfigure(1, weight=1)
            self.content_frame.scrollable_frame.grid_columnconfigure(0, weight=1)

            if products:
                for product in products:
                    treeview.insert("", "end", values=product)
            else:
                print("No products returned from the database query.")

        except OperationalError as e:
            print(f"Database Error: {e}")
            # Handle the database operational error as needed

        except Exception as e:
            print(f"An error occurred while fetching products: {e}")
           
            
            
        def export():
            export_to_csv(products, "products.csv")
            messagebox.showinfo("Success", "Products exported successfully.")

        def delete():
            selected_item = treeview.selection()
            if selected_item:
                item = treeview.item(selected_item)['values']
                confirm_delete_product(str(item[0]), item[1])
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

        def search():
            search_product_window()
        
        ctk.CTkButton(self.content_frame.scrollable_frame, text="Modify Product", command=modify).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(self.content_frame.scrollable_frame, text="Search Product", command=search).grid(row=4, column=0, padx=20, pady=10)
        ctk.CTkButton(self.content_frame.scrollable_frame, text="Export to CSV", command=export,fg_color="green").grid(row=5, column=0, padx=20, pady=10)
        ctk.CTkButton(self.content_frame.scrollable_frame, text="Delete Product", command=delete, fg_color="red").grid(row=6, column=0, padx=20, pady=10)

                
    import psycopg2
    from psycopg2 import OperationalError
    conn = psycopg2.connect(
        dbname="okzegkwz",
        user="okzegkwz",
        password="7UwFflnPy3byudSr32K1ugHniRSVK6v_",
        host="kandula.db.elephantsql.com",
        port="5432"
    )
    # Function to display the employees list
    def show_view_employees(self):

        try:
            print("Manage clicked")
            manage_window = ctk.CTkToplevel()  # Create a new top-level window using ctk.CTkToplevel
            app = ManageUsersApp(manage_window)  # Create an instance of ManageUsersApp
            manage_window.mainloop()  # Start the main loop for the management window
        except Exception as e:
            print(f"Error during manage: {e}")
       

       

    # Function to clear the content frame
    def clear_content_frame(self):

        for widget in self.content_frame.scrollable_frame.winfo_children():
            widget.destroy()
            

    # Function to confirm logout

    def confirm_logout(self):
        try:
            import datetime
            import logging
            logging.info("Attempting to log out user: %s", self.username)
            cursor = self.conn.cursor()
            current_time = datetime.datetime.now()
            logging.info("Current time: %s", current_time)

            # Update time_stamp_out with current_time
            cursor.execute("""
                UPDATE users
                SET time_stamp_out = %s
                WHERE user_name = %s;
            """, (current_time, self.username))

            # Verify if the update worked
            cursor.execute("SELECT time_stamp_out FROM users WHERE user_name = %s;", (self.username,))
            result = cursor.fetchone()
            logging.info("Updated time_stamp_out: %s", result)

            # Update working_hours using INTERVAL
            cursor.execute("""
                UPDATE users
                SET working_hours = COALESCE(working_hours, '0'::interval) + (time_stamp_out - time_stamp_in)
                WHERE user_name = %s;
            """, (self.username,))
            self.conn.commit()
            self.cursor.close()
            
            messagebox.showinfo("Logout", "Logged out successfully!")

        except Exception as e:
            self.conn.rollback()  # Rollback transaction on error to maintain data integrity
            logging.error("Logout Error: %s", str(e))
            messagebox.showerror("Logout Error", f"Logout Error: {str(e)}")

        finally:
            logging.info("Destroying the current window and redirecting to the login page.")
            self.destroy()
            try:
                import main_page
                main_page.initialize_login_ui(self)
            except Exception as e:
                logging.error("Redirection Error: %s", str(e))
                messagebox.showerror("Redirection Error", f"Redirection Error: {str(e)}")

            
def load_BGImg(app, light_image_path):
    try:
        light_image = Image.open(light_image_path).resize((300, 860))
        my_image = ctk.CTkImage(light_image=light_image, size=(300, 860))
        image_label = ctk.CTkLabel(app, image=my_image, text="")
        image_label.grid(row=0, column=0, sticky="nsew")
    except IOError as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")

# Main function to run the application
def main():
    app = ManegerPage('username')
    app.mainloop()

if __name__ == "__main__":
    main()