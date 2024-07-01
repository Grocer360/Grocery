import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2

class CartManagementApp:
    def __init__(self, container):
        self.container = container
        
        # Connect to the PostgreSQL database
        self.conn = self.connect_to_db()
        self.cursor = self.conn.cursor()

        # Frame to hold the cart entry fields
        self.cart_frame = ttk.Frame(self.container, padding="20")
        self.cart_frame.pack(padx=20, pady=20)

        # QR Code Entry Field
        ttk.Label(self.cart_frame, text="Product QR Code:").grid(row=0, column=0, sticky="w")
        self.qr_entry = ttk.Entry(self.cart_frame, width=30)
        self.qr_entry.grid(row=0, column=1, padx=10, pady=5)
        self.qr_entry.bind('<Return>', self.lookup_and_add_product)

        # Quantity Entry Field
        ttk.Label(self.cart_frame, text="Quantity:").grid(row=1, column=0, sticky="w")
        self.quantity_entry = ttk.Entry(self.cart_frame, width=10)
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5)
        self.quantity_entry.insert(0, "1")

        # Buttons
        self.process_transaction_button = ttk.Button(self.cart_frame, text="Process Transaction", command=self.process_transaction)
        self.process_transaction_button.grid(row=2, column=0, padx=10, pady=10)

        self.print_receipt_button = ttk.Button(self.cart_frame, text="Print Receipt", command=self.print_receipt)
        self.print_receipt_button.grid(row=2, column=1, padx=10, pady=10)

        # Treeview to display cart items
        self.cart_tree = ttk.Treeview(self.container, columns=("Name", "Price", "Quantity", "Total"), show="headings", height=10)
        self.cart_tree.heading("Name", text="Name")
        self.cart_tree.heading("Price", text="Price")
        self.cart_tree.heading("Quantity", text="Quantity")
        self.cart_tree.heading("Total", text="Total")
        self.cart_tree.pack(padx=20, pady=(0, 20))

        # Total price label
        self.total_label = ttk.Label(self.container, text="Total: $0.00")
        self.total_label.pack(pady=10)

        self.total_price = 0.00

    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                dbname="grocery_database_system",
                user="anas",
                password="0000",
                host="localhost",
                port="5432"
            )
            return conn
        except Exception as e:
            messagebox.showerror("Database Connection Error", str(e))
            self.container.destroy()

    def lookup_and_add_product(self, event=None):
        qr_code = self.qr_entry.get()
        try:
            self.cursor.execute("SELECT product_name, price FROM products WHERE qr_code = %s", (qr_code,))
            product = self.cursor.fetchone()

            if product:
                product_name = product[0]
                price = float(product[1])
                quantity = int(self.quantity_entry.get())
                total = price * quantity

                # Insert into Treeview
                self.cart_tree.insert("", "end", values=(product_name, price, quantity, total))

                # Update total price
                self.total_price += total
                self.total_label.config(text=f"Total: ${self.total_price:.2f}")

                # Clear entry fields
                self.clear_entries()
            else:
                messagebox.showerror("Error", "Product not found in database. Please add it in the Product Management page.")
                self.clear_entries()
        except Exception as e:
            messagebox.showerror("Database Query Error", str(e))

    def process_transaction(self):
        # Here, you can implement logic to process the transaction (e.g., saving to a database)
        messagebox.showinfo("Transaction", "Transaction processed successfully!")
        self.cart_tree.delete(*self.cart_tree.get_children())
        self.total_price = 0.00
        self.total_label.config(text="Total: $0.00")

    def print_receipt(self):
        items = self.cart_tree.get_children()
        receipt = "Receipt:\n\n"
        for item in items:
            item_values = self.cart_tree.item(item, "values")
            receipt += f"{item_values[0]} - ${item_values[1]} x {item_values[2]} = ${item_values[3]}\n"
        receipt += f"\nTotal: ${self.total_price:.2f}"
        messagebox.showinfo("Receipt", receipt)

    def clear_entries(self):
        self.qr_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, "1")

if __name__ == "__main__":
    root = tk.Tk()
    app = CartManagementApp(root)
    root.mainloop()


