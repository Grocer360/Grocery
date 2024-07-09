import sqlite3
import psycopg2
import cv2
from psycopg2 import sql
import ctypes
from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import customtkinter as ctk
import logging
import csv
import hashlib
from pyzbar.pyzbar import decode
import threading
from datetime import datetime, timedelta
from tkinter import messagebox
import csv
import simpleaudio as sa
from functools import partial

# Set CustomTkinter appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Initialize logging configuration
logging.basicConfig(filename='supermarket.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to log actions
def log_action(action):
    logging.info(action)

def log_error(error):
    logging.error(error)

# Define colors
colors = {
    "forest_green": "#228B22",
    "crimson_red": "#DC143C",
    "ocean_blue": "#1E90FF",
    "gold": "#FFD700",
    "amber_orange": "#FFBF00",
    "steel_gray": "#708090",
    "ivory_white": "#FFFFF0",
    "light_slate_gray": "#778899",
    "teal": "#008080",
    "plum": "#DDA0DD",
    "charcoal_black": "#36454F",
    "graphite_gray": "#4B515D",
}

global detected_products
detected_products = []

# Main application class using CustomTkinter
class SellerPage(ctk.CTk):
    def __init__(self, username):
        super().__init__()

        self.geometry('1280x720')
        self.after(10, self.fullscreen_and_disable_resize)
        self.title(f"Supermarket Management System - Welcome {username}")

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=2, sticky="nw", pady=90, padx=10)

        self.table_inner_frame = ctk.CTkFrame(self.content_frame)
        self.table_inner_frame.grid(row=0, column=0, padx=150, pady=5, sticky="n")

        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.grid(row=0, column=1, sticky="nw", pady=90, padx=10)

        self.status_label = ctk.CTkLabel(self.nav_frame, text="Selling Status", font=("Helvetica", 16))
        self.status_label.grid(row=10, column=0, columnspan=2, pady=10)

        load_BGImg(self, 'adminBG.png', 'adminBG.png')

        self.btn_add_product = ctk.CTkButton(self.nav_frame, text="Scan", command=self.process_barcodes, width=150, height=50)
        self.btn_add_product.grid(row=0, column=0, padx=20, pady=20)

        self.btn_add_employee = ctk.CTkButton(self.nav_frame, text="view receipt", command=self.view_receipt, width=150, height=50)
        self.btn_add_employee.grid(row=1, column=0, padx=20, pady=20)

        self.btn_view_products = ctk.CTkButton(self.nav_frame, text="Add Products", command=self.product_info_entry, width=150, height=50)
        self.btn_view_products.grid(row=2, column=0, padx=20, pady=20)

        # self.btn_view_employees = ctk.CTkButton(self.nav_frame, text="View Employees", command=self.show_view_employees, width=150, height=50)
        # self.btn_view_employees.grid(row=3, column=0, padx=20, pady=20)

        # self.btn_search_product = ctk.CTkButton(self.nav_frame, text="Search Product", command=self.show_search_product, width=150, height=50)
        # self.btn_search_product.grid(row=4, column=0, padx=20, pady=20)

        self.btn_logout = ctk.CTkButton(self.nav_frame, text="Logout", command=self.confirm_logout, fg_color="red")
        self.btn_logout.grid(row=5, column=0, padx=20, pady=20)

        self.conn = self.connect_to_db()
        self.columns = ["ProdName", "Quantity", "Category", "Price", "Total"]
        for i, col in enumerate(self.columns):
            col_label = ctk.CTkLabel(self.table_inner_frame, text=col, width=100, height=25, anchor="w", text_color="white")
            col_label.grid(row=0, column=i, padx=5, pady=5)

    # Database connection setup
    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                dbname="okzegkwz",
                user="okzegkwz",
                password="7UwFflnPy3byudSr32K1ugHniRSVK6v_",
                host="kandula.db.elephantsql.com",
                port="5432"
            )
            return conn
        except Exception as e:
            self.status_label.configure(text=f"Database Connection Error: {str(e)}")
            return None

    # Function to enable fullscreen mode and disable resizing
    def fullscreen_and_disable_resize(self):
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

    # Function to clear the content frame
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # Function to display the add product form
    def product_info_entry(self):
        self.clear_content_frame()

        ctk.CTkLabel(self.content_frame, text="The Product Info", font=("Arial", 24)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        ctk.CTkLabel(self.content_frame, text="Barcode:").grid(row=1, column=0, sticky="nw", padx=20, pady=5)
        self.barCode_entry = ctk.CTkEntry(self.content_frame)
        self.barCode_entry.grid(row=1, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Product Name:").grid(row=2, column=0, sticky="nw", padx=20, pady=5)
        self.name_entry = ctk.CTkEntry(self.content_frame)
        self.name_entry.grid(row=2, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Category:").grid(row=3, column=0, sticky="nw", padx=20, pady=5)
        self.category_entry = ctk.CTkEntry(self.content_frame)
        self.category_entry.grid(row=3, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Price:").grid(row=4, column=0, sticky="nw", padx=20, pady=5)
        self.price_entry = ctk.CTkEntry(self.content_frame)
        self.price_entry.grid(row=4, column=1, padx=20, pady=5)

        ctk.CTkLabel(self.content_frame, text="Quantity:").grid(row=5, column=0, sticky="nw", padx=20, pady=5)
        self.quantity_entry = ctk.CTkEntry(self.content_frame)
        self.quantity_entry.grid(row=5, column=1, padx=20, pady=5)

        ctk.CTkButton(self.content_frame, text="Add to Receipt", command=self.add_product_to_db).grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky="n")
        ctk.CTkButton(self.content_frame, text="Cancel", command=self.cancel_order, fg_color="red").grid(row=7, column=0, columnspan=2, padx=20, pady=10, sticky="n")
        ctk.CTkButton(self.content_frame, text="Print Receipt", command=self.print_receipt).grid(row=8, column=0, columnspan=2, padx=20, pady=10, sticky="n")

        # Add product labels and entry fields centered within their boxes
        labels_texts = ["Bar Code", "Name", "Category", "Quantity", "Price"]
        entry_widgets = {}
        for i, text in enumerate(labels_texts):
            label = ctk.CTkLabel(self.main_frame, text=text, text_color="white")
            label.grid(row=i+4, column=0, pady=4, padx=(510, 5), sticky="e")

            entry = ctk.CTkEntry(self.main_frame)
            entry.grid(row=i+4, column=1, pady=5, padx=(3, 20), sticky="w")
            entry_widgets[text] = entry

        # Define individual entry variables
        self.barCode_entry = entry_widgets["Bar Code"]
        self.name_entry = entry_widgets["Name"]
        self.category_entry = entry_widgets["Category"]
        self.quantity_entry = entry_widgets["Quantity"]
        self.price_entry = entry_widgets["Price"]

    # Function to add the product to database
    def add_product_to_db(self):
        bar_code = self.barCode_entry.get()
        name = self.name_entry.get()
        quantity = self.quantity_entry.get()
        category = self.category_entry.get()
        price = self.price_entry.get()

        if not (bar_code and name and quantity and category and price):
            self.status_label.configure(text="All fields must be filled.")
            return

        try:
            quantity = int(quantity)
            price = float(price)

        except ValueError:
            self.status_label.configure(text="Quantity must be an integer and Price must be a float.")
            return

        try:
            cursor = self.conn.cursor()
            insert_query = "INSERT INTO products (bar_code, prod_name, quantity, category, price) VALUES (%s, %s, %s, %s, %s)"

            cursor.execute(insert_query, (bar_code, name, quantity, category, price))
            self.conn.commit()
            cursor.close()
            self.status_label.configure(text="Product added successfully!")
        except Exception as e:
            self.status_label.configure(text=f"Database Error: {str(e)}")

    # Add product button
    def add_product_button_action(self):
        self.add_product_to_db()

    def view_receipt(self):
        self.clear_content_frame()
        ctk.CTkLabel(self.content_frame, text="View Products", font=("Arial", 24)).grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nw")
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            cursor.close()

            columns = ("ProdName", "Quantity", "Category", "Price", "Total")
            tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
            for product in products:
                tree.insert("", "end", values=product)
            tree.grid(row=1, column=0, columnspan=2, padx=20, pady=20)
        except Exception as e:
            self.status_label.configure(text=f"Database Error: {str(e)}")
            return

        # Calculate total receipt value and display
        total_receipt = self.calculate_total_receipt()
        total_receipt_label = ctk.CTkLabel(self.content_frame, text=f"Total Receipt: {total_receipt:.2f}", width=100, height=25, anchor="w", text_color="white")
        total_receipt_label.grid(row=6, column=0, columnspan=2, padx=20, pady=10)


    def update_quantity(self, event, row_index):
        try:
            new_quantity = int(event.widget.get())
            product = list(detected_products[row_index - 1])
            product[1] = new_quantity
            product[4] = new_quantity * product[3]
            detected_products[row_index - 1] = tuple(product)
            self.update_product_table()
        except ValueError:
            self.status_label.configure(text="Invalid quantity entered.")
  
    # Function to clear the content frame
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def log_out(self, username):
        try:
            cursor = self.conn.cursor()
            current_time = datetime.now()
            cursor.execute("UPDATE Users SET logged_in = %s, time_stamp_out = %s WHERE user_name = %s", (False, current_time, username))
            self.conn.commit()
            cursor.close()
            self.status_label.configure(text="Logged out successfully!")

            # Calculate and log working hours
            self.calculate_working_hours(username)

        except Exception as e:
            self.status_label.configure(text=f"Logout Error: {str(e)}")
        finally:
            self.destroy()

    # Function to confirm logout
    def confirm_logout(self):
        response = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if response:
            self.conn.close()
            self.destroy()

    # ctk.CTkButton(self.modify_window, text="Update", command=submit).grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    # def update_treeview_receipt(self):
    #     # Clear current content in the table
    #     for child in self.treeview.get_children():
    #         self.treeview.delete(child)

    #     # Define columns in the Treeview
    #     self.treeview["columns"] = self.columns
    #     self.treeview.heading("#0", text="Index")
    #     for col in self.columns:
    #         self.treeview.heading(col, text=col)

    #     # Add detected products to the Treeview
    #     for index, product in enumerate(detected_products, start=1):
    #         self.treeview.insert("", "end", text=index, values=product)


    def update_quantity(self, event, row_index):
        try:
            new_quantity = int(event.widget.get())
            product = list(detected_products[row_index - 1])
            product[1] = new_quantity
            product[4] = new_quantity * product[3]
            detected_products[row_index - 1] = tuple(product)
            self.update_product_table()
        except ValueError:
            self.status_label.configure(text="Invalid quantity entered.")

    def read_data_base(self, cursor, barCode):
        try:
            query = "SELECT prod_name, quantity, category, price FROM Products WHERE bar_code = %s;"
            cursor.execute(query, (barCode,))
            product = cursor.fetchone()

            if product:
                existing_product = next((p for p in detected_products if p[0] == product[0]), None)
                if existing_product:
                    detected_products = [
                        (p[0], p[1] + 1 if p == existing_product else p[1], p[2], p[3], (p[1] + 1) * p[3] if p == existing_product else p[4])
                        for p in detected_products
                    ]
                else:
                    detected_products.append((product[0], 1, product[2], product[3], product[3]))

                self.update_product_table()
                self.barCode_entry.delete(0,'end')
                self.barCode_entry.insert(0,barCode)
                
            else:
                self.status_label.configure(text="Product not found in database.")

        except Exception as e:
            self.status_label.configure(text=f"Database Error: {str(e)}")

    def barcode_decoder(self, image):
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray_img)
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            return barcode_data
        return None

    # Function to process barcodes
    def process_barcodes(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                self.status_label.configure(text="Failed to grab frame from camera.")
                break

            barcode_data = self.barcode_decoder(frame)
            if barcode_data:
                # threading.Thread(target=self.play_beep_sound).start()  # Play beep sound in a separate thread
                self.status_label.configure(text=f"Detected Barcode: {barcode_data}")
                self.barCode_entry.insert(0, barcode_data)
                self.barCode_entry.configure(state="disabled")
                cursor = self.conn.cursor()
                self.read_data_base(cursor, barcode_data)
                cv2.waitKey(1000)

            cv2.imshow("Barcode Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    # Start camera when the application is opened
    def start_camera(self):
        camera_thread = threading.Thread(target=self.process_barcodes)
        camera_thread.daemon = True
        camera_thread.start()

    def calculate_total_receipt(self, detected_products):
        total = sum(product[4] for product in detected_products)
        return total

    # Function to play beep sound
    def play_beep_sound(self):
        try:
            wave_obj = sa.WaveObject.from_wave_file("beeeeb.wav")
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except Exception as e:
            self.status_label.configure(text=f"Sound Error: {str(e)}")
                
    def update_product_table(self):
            # Clear current content in the table
            for widget in self.table_inner_frame.winfo_children():
                widget.destroy()

            # Add headers
            for i, col in enumerate(self.columns):
                col_label = ctk.CTkLabel(self.table_inner_frame, text=col, width=100, height=25, anchor="w", text_color="white")
                col_label.grid(row=0, column=i, padx=5, pady=5)
            
            # Add detected products to the table
            for row_index, product in enumerate(detected_products, start=1):
                for col_index, value in enumerate(product):
                    if col_index == 1:  # Quantity column
                        self.quantity_entry = ctk.CTkEntry(self.table_inner_frame, width=100)
                        self.quantity_entry.insert(0, value)
                        self.quantity_entry.grid(row=row_index, column=col_index, padx=5, pady=5)
                        self.quantity_entry.bind("<Return>", partial(self.update_quantity, row_index=row_index))
                    else:
                        data_label = ctk.CTkLabel(self.table_inner_frame, text=value, width=100, height=25, anchor="w", text_color="white")
                        data_label.grid(row=row_index, column=col_index, padx=5, pady=5)

            # Calculate and display total receipt value
            total_receipt = self.calculate_total_receipt()
            total_receipt_label = ctk.CTkLabel(self.table_inner_frame, text=f"Total Receipt: {total_receipt:.2f}", width=100, height=25, anchor="w", text_color="white")
            total_receipt_label.grid(row=len(detected_products) + 1, column=0, columnspan=len(self.columns), padx=5, pady=5)


    def save_receipt_to_file(self, cursor,products, username):
        with open('receipt.csv', 'a', newline='') as csvfile:
            fieldnames = ['seller','ProdName', 'Quantity', 'Category', 'Price', 'Total','working_Hours']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if csvfile.tell() == 0:
                writer.writeheader()
                query = "SELECT working_hours FROM users WHERE user_name = %s;"
                cursor.execute(query, (username,))
                hours = cursor.fetchone()

            for product in products:
                writer.writerow({
                    'ProdName': product[0],
                    'Quantity': product[1],
                    'Category': product[2],
                    'Price': product[3],
                    'Total': product[4],
                    'seller':username,
                    'working_Hours':hours
                })


    # Function to print the receipt
    def print_receipt(self):
        filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.columns)
            writer.writerows(self.detected_products)
        self.status_label.configure(text=f"Receipt printed: {filename}")


    # Function to cancel the current order
    def cancel_order(self):
        self.detected_products = []
        self.clear_content_frame()
        self.status_label.configure(text="Order canceled.")

    def calculate_working_hours(self, username):
        try:
            cursor = self.conn.cursor()
            query = "SELECT time_stamp_in, time_stamp_out, working_hours FROM Users WHERE user_name = %s;"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if result:
                time_in, time_out, hours = result
                if time_in and time_out:
                    # Calculate the new working hours
                    current_working_hours = hours or timedelta(0)  # Initialize to 0 if hours is None
                    new_working_hours = (time_out - time_in) + current_working_hours
                    
                    # Update the database with the new working hours
                    update_query = "UPDATE Users SET working_hours = %s WHERE user_name = %s;"
                    cursor.execute(update_query, (new_working_hours, username))
                    self.conn.commit()
                    
                    return new_working_hours
                else:
                    return timedelta(0)  # Return zero if either time_in or time_out is None
            else:
                return timedelta(0)  # User not found scenario

        except Exception as e:
            self.status_label.configure(text=f"Error calculating working hours: {str(e)}")

        finally:
            cursor.close()
    

def load_BGImg(app, light_image_path):
    try:
        light_image = Image.open(light_image_path).resize((400, 860))
        my_image = ctk.CTkImage(light_image=light_image, size=(400, 860))
        image_label = ctk.CTkLabel(app, image=my_image, text="")
        image_label.grid(row=0, column=0, sticky="nsew")
    except IOError as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")



# Main function to run the application
def main():
    # Example: Get the username from user input or another method
    username = "example_user"
    app = SellerPage(username)
    app.mainloop()

if __name__ == "__main__":
    main()
