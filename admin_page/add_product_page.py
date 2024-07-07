import customtkinter as ctk
import psycopg2
from tkinter import messagebox

class AddProductPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure_design()

    def configure_design(self):
        self.add_label("Add Products Page")
        
        # Bar code entry
        self.bar_code_label = ctk.CTkLabel(self, text="Bar Code")
        self.bar_code_label.pack(pady=5)
        self.bar_code_entry = ctk.CTkEntry(self)
        self.bar_code_entry.pack(pady=5)
        
        # Product name entry
        self.prod_name_label = ctk.CTkLabel(self, text="Product Name")
        self.prod_name_label.pack(pady=5)
        self.prod_name_entry = ctk.CTkEntry(self)
        self.prod_name_entry.pack(pady=5)
        
        # Quantity entry
        self.quantity_label = ctk.CTkLabel(self, text="Quantity")
        self.quantity_label.pack(pady=5)
        self.quantity_entry = ctk.CTkEntry(self)
        self.quantity_entry.pack(pady=5)
        
        # Category entry
        self.category_label = ctk.CTkLabel(self, text="Category")
        self.category_label.pack(pady=5)
        self.category_entry = ctk.CTkEntry(self)
        self.category_entry.pack(pady=5)
        
        # Price entry
        self.price_label = ctk.CTkLabel(self, text="Price")
        self.price_label.pack(pady=5)
        self.price_entry = ctk.CTkEntry(self)
        self.price_entry.pack(pady=5)
        
        # Submit button
        self.submit_button = ctk.CTkButton(self, text="Add Product", command=self.add_product)
        self.submit_button.pack(pady=20)

    def add_label(self, text):
        label = ctk.CTkLabel(self, text=text, font=("Helvetica", 24))
        label.pack(pady=20)
        return label

    def add_product(self):
        bar_code = self.bar_code_entry.get()
        prod_name = self.prod_name_entry.get()
        quantity = self.quantity_entry.get()
        category = self.category_entry.get()
        price = self.price_entry.get()
        
        if not all([bar_code, prod_name, quantity, category, price]):
            messagebox.showerror("Input Error", "All fields are required")
            return

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be an integer and Price must be a number")
            return
        
        # Database connection
        try:
            conn = psycopg2.connect(
                dbname="grocery_database_system",
                user="anas",
                password="0000",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()
            
            query = """
            INSERT INTO products (bar_code, prod_name, quantity, category, price)
            VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (bar_code, prod_name, quantity, category, price))
            
            conn.commit()
            cur.close()
            conn.close()
            
            messagebox.showinfo("Success", "Product added successfully")
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def clear_entries(self):
        self.bar_code_entry.delete(0, 'end')
        self.prod_name_entry.delete(0, 'end')
        self.quantity_entry.delete(0, 'end')
        self.category_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')


