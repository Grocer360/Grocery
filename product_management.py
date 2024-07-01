import tkinter as tk
from tkinter import ttk
import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="grocery_database_system",
        user="anas",
        password="0000",
        host="localhost",
        port="5432"
    )

class ProductManagementApp:
    def __init__(self, container):
        self.parent = container
        
        # Frame to hold the product entry fields
        self.product_frame = ttk.Frame(self.parent, padding="20")
        self.product_frame.pack(padx=20, pady=20)
        
        # Product Details Entry Fields
        ttk.Label(self.product_frame, text="Product Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(self.product_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.product_frame, text="Price:").grid(row=1, column=0, sticky="w")
        self.price_entry = ttk.Entry(self.product_frame, width=10)
        self.price_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.product_frame, text="QR Code:").grid(row=2, column=0, sticky="w")
        self.qr_entry = ttk.Entry(self.product_frame, width=30)
        self.qr_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Buttons
        self.add_button = ttk.Button(self.product_frame, text="Add Product", command=self.add_product)
        self.add_button.grid(row=3, column=0, padx=10, pady=10)
        
        self.delete_button = ttk.Button(self.product_frame, text="Delete Product", command=self.delete_product)
        self.delete_button.grid(row=3, column=1, padx=10, pady=10)
        
        # Treeview to display products
        self.product_tree = ttk.Treeview(self.parent, columns=("Name", "Price", "QR Code"), show="headings", height=10)
        self.product_tree.heading("Name", text="Name")
        self.product_tree.heading("Price", text="Price")
        self.product_tree.heading("QR Code", text="QR Code")
        self.product_tree.pack(padx=20, pady=(0, 20))
        
        # Fetch and display products from the database
        self.fetch_and_display_products()
    
    def fetch_and_display_products(self):
        # Clear the current contents of the Treeview
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Fetch products from the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT product_name, price, qr_code FROM products")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Insert products into the Treeview
        for product in products:
            self.product_tree.insert("", "end", values=product)
    
    def add_product(self):
        name = self.name_entry.get()
        price = self.price_entry.get()
        qr_code = self.qr_entry.get()
        
        # Add to the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (product_name, price, qr_code) VALUES (%s, %s, %s)",
            (name, price, qr_code)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # Insert into Treeview
        self.product_tree.insert("", "end", values=(name, price, qr_code))
        
        # Clear entry fields
        self.clear_entries()
    
    def delete_product(self):
        selected_item = self.product_tree.selection()
        if selected_item:
            item_values = self.product_tree.item(selected_item, "values")
            qr_code = item_values[2]
            
            # Delete from the database
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE qr_code = %s", (qr_code,))
            conn.commit()
            cursor.close()
            conn.close()
            
            # Delete from the Treeview
            self.product_tree.delete(selected_item)
            
            # Clear entry fields
            self.clear_entries()
    
    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.qr_entry.delete(0, tk.END)


# import tkinter as tk
# from tkinter import ttk
# import psycopg2

# def connect_db():
#     return psycopg2.connect(
#         dbname="grocery_database_system",
#         user="anas",
#         password="0000",
#         host="localhost",
#         port="5432"
#     )

# class ProductManagementApp:
#     def __init__(self, parent):
#         self.parent = parent
#         # self.parent.title("Product Management")
        
#         # Frame to hold the product entry fields
#         self.product_frame = ttk.Frame(self.parent, padding="20")
#         self.product_frame.pack(padx=20, pady=20)
        
#         # Product Details Entry Fields
#         ttk.Label(self.product_frame, text="Product Name:").grid(row=0, column=0, sticky="w")
#         self.name_entry = ttk.Entry(self.product_frame, width=30)
#         self.name_entry.grid(row=0, column=1, padx=10, pady=5)
        
#         ttk.Label(self.product_frame, text="Price:").grid(row=1, column=0, sticky="w")
#         self.price_entry = ttk.Entry(self.product_frame, width=10)
#         self.price_entry.grid(row=1, column=1, padx=10, pady=5)
        
#         ttk.Label(self.product_frame, text="QR Code:").grid(row=3, column=0, sticky="w")
#         self.qr_entry = ttk.Entry(self.product_frame, width=30)
#         self.qr_entry.grid(row=3, column=1, padx=10, pady=5)
        
#         # Buttons
#         self.add_button = ttk.Button(self.product_frame, text="Add Product", command=self.add_product)
#         self.add_button.grid(row=4, column=0, padx=10, pady=10)
        
#         self.edit_button = ttk.Button(self.product_frame, text="Edit Product", command=self.edit_product)
#         self.edit_button.grid(row=4, column=1, padx=10, pady=10)
        
#         self.delete_button = ttk.Button(self.product_frame, text="Delete Product", command=self.delete_product)
#         self.delete_button.grid(row=4, column=2, padx=10, pady=10)
        
#         # Treeview to display products
#         self.product_tree = ttk.Treeview(self.parent, columns=("Name", "Price", "QR Code"), show="headings", height=10)
#         self.product_tree.heading("Name", text="Name")
#         self.product_tree.heading("Price", text="Price")
#         self.product_tree.heading("QR Code", text="QR Code")
#         self.product_tree.pack(padx=20, pady=(0, 20))
        
#         # Fetch and display products from the database
#         self.fetch_and_display_products()
    
#     def fetch_and_display_products(self):
#         # Clear the current contents of the Treeview
#         for item in self.product_tree.get_children():
#             self.product_tree.delete(item)
        
#         # Fetch products from the database
#         conn = connect_db()
#         cursor = conn.cursor()
#         cursor.execute("SELECT product_name, price, qr_code FROM products")
#         products = cursor.fetchall()
#         cursor.close()
#         conn.close()
        
#         # Insert products into the Treeview
#         for product in products:
#             self.product_tree.insert("", "end", values=product)
    
#     def add_product(self):
#         name = self.name_entry.get()
#         price = self.price_entry.get()
#         qr_code = self.qr_entry.get()
        
#         # Add to the database
#         conn = connect_db()
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO products (product_name, price, qr_code) VALUES (%s, %s, %s)",
#             (name, price, qr_code)
#         )
#         conn.commit()
#         cursor.close()
#         conn.close()
        
#         # Insert into Treeview
#         self.product_tree.insert("", "end", values=(name, price, qr_code))
        
#         # Clear entry fields
#         self.clear_entries()
    
#     def edit_product(self):
#         selected_item = self.product_tree.selection()
#         if selected_item:
#             # Update selected item
#             self.product_tree.item(selected_item, values=(
#                 self.name_entry.get(),
#                 self.price_entry.get(),
#                 self.qr_entry.get()
#             ))
#             # Clear entry fields
#             self.clear_entries()
    
#     def delete_product(self):
#         selected_item = self.product_tree.selection()
#         if selected_item:
#             item_values = self.product_tree.item(selected_item, "values")
#             qr_code = item_values[2]
            
#             # Delete from the database
#             conn = connect_db()
#             cursor = conn.cursor()
#             cursor.execute("DELETE FROM products WHERE qr_code = %s", (qr_code,))
#             conn.commit()
#             cursor.close()
#             conn.close()
            
#             # Delete from the Treeview
#             self.product_tree.delete(selected_item)
            
#             # Clear entry fields
#             self.clear_entries()
    
#     def clear_entries(self):
#         self.name_entry.delete(0, tk.END)
#         self.price_entry.delete(0, tk.END)
#         self.qr_entry.delete(0, tk.END)


