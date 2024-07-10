import customtkinter as ctk
import psycopg2
from psycopg2 import sql
import cv2
from pyzbar.pyzbar import decode
import threading

from tkinter import messagebox
import csv
# import simpleaudio as sa
from functools import partial
from datetime import datetime, timedelta, time
from tkinter import Scrollbar, Canvas
from PIL import Image, ImageTk


def initialize_seller_page(username,top,parent):
    top.destroy()
    parent.destroy()
    # Initialize the main window
    app = ctk.CTk()
    app.geometry("800x600")
    app.title(f"Supermarket Management System - Welcome {username}")

    # Set custom colors and styles
    ctk.set_default_color_theme("dark-blue")
    ctk.set_appearance_mode("dark")

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

    # Database connection setup
    def connect_to_db():
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
            status_label.configure(text=f"Database Connection Error: {str(e)}")
            return None

    conn = connect_to_db()

    from datetime import datetime

    def log_out():
        try:
            cursor = conn.cursor()
            current_time = datetime.now()            

            # Update time_stamp_out with current_time
            cursor.execute("""
                UPDATE users
                SET time_stamp_out = %s
                WHERE user_name = %s;
            """, (current_time, username))

            # Update working_hours using INTERVAL
            cursor.execute("""
                UPDATE users
                SET working_hours = COALESCE(working_hours, '0'::interval) + (time_stamp_out - time_stamp_in)
                WHERE user_name = %s;
            """, (username,))
            conn.commit()
            cursor.close()

            messagebox.showinfo("Logout", f"Logged out successfully!")

        except Exception as e:
            conn.rollback()  # Rollback transaction on error to maintain data integrity
            messagebox.showerror("Logout Error", f"Logout Error: {str(e)}")

        finally:
            # You might want to destroy the app window after logout
            app.destroy()
            import main_page
            main_page.initialize_login_ui(app)

    # Function to add product to database
    def add_product_to_db():
        global detected_products

        bar_code = barcode_entry.get()
        name = name_entry.get()
        quantity = quantity_entry.get()
        category = category_entry.get()
        price = price_entry.get()

        if not (bar_code and name and quantity and category and price):
            status_label.configure(text="All fields must be filled.")
            return

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            status_label.configure(text="Quantity must be an integer and Price must be a float.")
            return

        try:
            cursor = conn.cursor()
            insert_query = sql.SQL("""
                INSERT INTO products (bar_code, prod_name, quantity, category, price)
                VALUES (%s, %s, %s, %s, %s)
            """)
            cursor.execute(insert_query, (bar_code, name, quantity, category, price))
            conn.commit()
            cursor.close()
            status_label.configure(text="Product added successfully!")
            bar_code = barcode_entry.get()
            name_entry.insert(0,"") 
            quantity_entry.insert(0,"") 
            category_entry.insert(0,"")
            price_entry.insert(0,"")
        except Exception as e:
            status_label.configure(text=f"Database Error: {str(e)}")

    # Create and place the logo
    logo_label = ctk.CTkLabel(app, text=f"Welcome {username}", font=("Helvetica", 24, "bold"), text_color="white")
    logo_label.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

    # Create navigation buttons
    nav_frame = ctk.CTkFrame(app)
    nav_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nw")

    buttons = ["Logout"]
    for i, btn_text in enumerate(buttons):
        btn = ctk.CTkButton(nav_frame, text=btn_text, width=140, height=40, fg_color=colors["crimson_red"], text_color="white", command=log_out)
        btn.grid(row=i, column=0, pady=5)

    # Create main content frame
    main_frame = ctk.CTkFrame(app, corner_radius=10)
    main_frame.grid(row=1, column=5, rowspan=2, padx=20, pady=20, sticky="nsew")

    status_label = ctk.CTkLabel(main_frame, text="Selling Status", font=("Helvetica", 16), text_color="white")
    status_label.grid(row=1, column=0, columnspan=2, pady=10)

    # Add product labels and entry fields centered within their boxes
    labels_texts = ["Bar Code", "Name", "Category", "Quantity", "Price"]
    entry_widgets = {}
    for i, text in enumerate(labels_texts):
        label = ctk.CTkLabel(main_frame, text=text, text_color="white")
        label.grid(row=i+4, column=0, pady=4, padx=(510, 5), sticky="e")

        entry = ctk.CTkEntry(main_frame)
        entry.grid(row=i+4, column=1, pady=5, padx=(3, 20), sticky="w")
        entry_widgets[text] = entry

    # Define individual entry variables
    barcode_entry = entry_widgets["Bar Code"]
    name_entry = entry_widgets["Name"]
    category_entry = entry_widgets["Category"]
    quantity_entry = entry_widgets["Quantity"]
    price_entry = entry_widgets["Price"]

    # Add product button
    def add_product_button_action():
        add_product_to_db()

    add_product_btn = ctk.CTkButton(main_frame, text="Add Product", fg_color=colors["forest_green"], text_color="white", command=add_product_button_action)
    add_product_btn.grid(row=8, column=0, pady=10, columnspan=2)

    # Create a table for product details
    table_frame = ctk.CTkFrame(main_frame)
    table_frame.grid(row=12, column=0, columnspan=3, pady=20, sticky="nsew")

    # Center the table within the frame
    table_frame.grid_columnconfigure(0, weight=1)
    table_frame.grid_rowconfigure(0, weight=1)

    table_inner_frame = ctk.CTkFrame(table_frame)
    table_inner_frame.grid(row=0, column=0, padx=150, pady=5, sticky="n")

    columns = ["ProdName", "Quantity", "Category", "Price", "Total"]
    for i, col in enumerate(columns):
        col_label = ctk.CTkLabel(table_inner_frame, text=col, width=100, height=25, anchor="w", text_color="white")
        col_label.grid(row=0, column=i, padx=5, pady=5)

    # List to hold detected products
    global detected_products
    detected_products = []
    global row_widgets
    row_widgets = {}
    def update_product_table():
        global detected_products

        total_receipt = calculate_total_receipt()
        if not total_receipt:
            total_label = ctk.CTkLabel(table_inner_frame, text=f"Total: {0}", width=100, height=25, anchor="w", text_color="white")

        for row_index, product in enumerate(detected_products, start=1):
            if row_index not in row_widgets:
                row_widgets[row_index] = {}
                for col_index, value in enumerate(product):
                    if col_index == 1:  # Quantity column
                        quantity_entry = ctk.CTkEntry(table_inner_frame, width=100)
                        quantity_entry.insert(0, value)
                        quantity_entry.grid(row=row_index, column=col_index, padx=25, pady=25)
                        quantity_entry.bind("<Return>", partial(update_quantity, row_index=row_index))
                        row_widgets[row_index][col_index] = quantity_entry
                    else:
                        data_label = ctk.CTkLabel(table_inner_frame, text=value, width=100, height=25, anchor="w", text_color="white")
                        data_label.grid(row=row_index, column=col_index, padx=25, pady=25)
                        row_widgets[row_index][col_index] = data_label

            for col_index, value in enumerate(product):
                if col_index in row_widgets[row_index]:
                    widget = row_widgets[row_index][col_index]
                    if col_index == 1:  # Quantity column
                        widget.delete(0, 'end')
                        widget.insert(0, value)
                    else:
                        widget.configure(text=value)
        # if total_label:
        #     total_label.destroy()
        total_label = ctk.CTkLabel(table_inner_frame, text=f"Total: ${total_receipt:.2f}", width=100, height=25, anchor="w", text_color="white")
        total_label.grid(row=len(detected_products) + 1, column=4, padx=25, pady=25)

    def check_database_quantity(barcode, requested_quantity):
        """Checks if there is sufficient quantity in the PostgreSQL database."""
        try:
            cursor = conn.cursor()

            # Use parameterized query for security
            query = sql.SQL("SELECT quantity FROM products WHERE bar_code = %s")
            cursor.execute(query, (barcode,))
            result = cursor.fetchone()

            if result:
                current_quantity = result[0]
                return requested_quantity <= current_quantity
            else:
                return False  # Product not found
        except psycopg2.Error as e:
            status_label.configure(text=f"Database Error: {str(e)}")
            return False  # Error handling
    
    def update_quantity(event, row_index):
        global detected_products

        try:
            new_quantity = int(event.widget.get())
            barcode = detected_products[row_index - 1][0]

            if not check_database_quantity(barcode, new_quantity, row_index):
                status_label.configure(text="Insufficient stock for this product.")
                return

            # Update the product tuple
            product = list(detected_products[row_index - 1])
            product[1] = new_quantity
            product[4] = new_quantity * product[3]
            detected_products[row_index - 1] = tuple(product)

            # Update database quantity
            try:
                cursor = conn.cursor()
                update_query = sql.SQL("UPDATE products SET quantity = quantity - %s WHERE bar_code = %s")
                cursor.execute(update_query, (new_quantity, barcode))
                conn.commit()
            except psycopg2.Error as e:
                status_label.configure(text=f"Database Error: {str(e)}")
                return  # Don't update table if database update failed

            update_product_table()  # Refresh the table

        except ValueError:
            status_label.configure(text="Invalid quantity entered.")
    # Function to read data from database based on barcode
    def read_data_base(cursor, barcode):
        global detected_products, low_stock_warnings
        low_stock_warnings = set()

        try:
            # Execute the query to get product details
            query = "SELECT prod_name, quantity, category, price FROM Products WHERE bar_code = %s;"
            cursor.execute(query, (barcode,))
            product = cursor.fetchone()

            # Clear and update the barcode entry field
            barcode_entry.delete(0, 'end')
            barcode_entry.insert(0, barcode)
            
            if product:
                product_name, quantity, category, price = product

                # Check if stock is low and show a warning if not already shown for this product
                if quantity <= 10 and product_name not in low_stock_warnings:
                    messagebox.showinfo("Low Stock", f"{product_name} quantity is less than 10.")
                    low_stock_warnings.add(product_name)

                existing_product = next((p for p in detected_products if p[0] == product_name), None)

                if existing_product:
                    # Calculate the new quantity and total price
                    new_quantity = existing_product[1] + 1
                    if new_quantity > quantity:
                        messagebox.showwarning("Insufficient Stock", f"Cannot add more {product_name}. Only {quantity} items available.")
                    else:
                        detected_products = [
                            (p[0], new_quantity if p == existing_product else p[1], p[2], p[3], new_quantity * p[3] if p == existing_product else p[4])
                            for p in detected_products
                        ]
                else:
                    if quantity < 1:
                        messagebox.showwarning("Out of Stock", f"{product_name} is out of stock.")
                    else:
                        detected_products.append((product_name, 1, category, price, price))
                
                # Update the product table with the latest data
                update_product_table()

            else:
                status_label.configure(text="Product not found in database.")
        except Exception as e:
            status_label.configure(text=f"Database Error: {str(e)}")

    # Initialize the set to track products that have shown low stock warnings


    def calculate_total_receipt():
        global detected_products
        total = sum(product[4] for product in detected_products)
        return total

    # Function to decode barcodes
    def barcode_decoder(image):
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray_img)
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            return barcode_data
        return None

    # Function to play beep sound
    def play_beep_sound():
        try:
            wave_obj = sa.WaveObject.from_wave_file("beeeeb.wav")
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except Exception as e:
            status_label.configure(text=f"Sound Error: {str(e)}")

    # Function to process barcodes
    def process_barcodes():
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                status_label.configure(text="Failed to grab frame from camera.")
                break

            barcode_data = barcode_decoder(frame)
            if barcode_data:
                threading.Thread(target=play_beep_sound).start()  # Play beep sound in a separate thread
                status_label.configure(text=f"Detected Barcode: {barcode_data}")
                cursor = conn.cursor()
                barcode_entry.insert(0, barcode_data)
                # barcode_entry.configure(state="disalbled")
                read_data_base(cursor, barcode_data)
                cv2.waitKey(1000)

            cv2.imshow("Barcode Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    # Start camera when the application is opened
    camera_thread = threading.Thread(target=process_barcodes)
    camera_thread.daemon = True
    camera_thread.start()

    # Create a frame for the bottom buttons and place it after the table
    bottom_frame = ctk.CTkFrame(main_frame)
    bottom_frame.grid(row=10, column=0, columnspan=3, pady=20)

    def save_receipt_to_file(products):
        
        # Check if the file exists and if it's empty
        try:
            with open('receipt.csv', 'r') as csvfile:
                reader = csv.reader(csvfile)
                file_empty = next(reader, None) is None
        except FileNotFoundError:
            file_empty = True

        with open('receipt.csv', 'a', newline='') as csvfile:
            fieldnames = ['ProdName', 'Quantity', 'Category', 'Price', 'Total', 'Seller','Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header only if the file is empty
            if file_empty:
                writer.writeheader()

            for product in products:
                writer.writerow({
                    'ProdName': product[0],
                    'Quantity': product[1],
                    'Category': product[2],
                    'Price': product[3],
                    'Total': product[4],
                    'Seller': username, # Include the seller's name
                    'Time' : datetime.now()  
                })

    def print_receipt():
        global detected_products
        global row_widgets

        # Destroy all widgets in row_widgets
        for row in row_widgets.values():
            for widget in row.values():
                widget.destroy()
        # temp_quan = 0
        # for product in detected_products:
        #     temp_quan = product[1]

        # conn.execute("UPDATE products SET quantity = %s, WHERE barcode = %s", (, current_time, username))
        # Save the receipt to file and show a message
        save_receipt_to_file(detected_products)
        messagebox.showinfo("Info", f"Receipt saved and printed by: {username}:\n{detected_products}")

        # Clear detected products and update the table
        detected_products = []
        row_widgets = {}
        update_product_table()

    def cancel_order():
        global detected_products
        global row_widgets

        # Destroy all widgets in row_widgets
        for row in row_widgets.values():
            for widget in row.values():
                widget.destroy()
        # Clear detected products and update the table
        detected_products = []
        row_widgets = {}
        update_product_table()

        # Show a message
        messagebox.showinfo("Info", "Order canceled and list cleared")


    bottom_buttons = ["Cancel", "Print"]
    for btn_text in bottom_buttons:
        color = colors["forest_green"] if btn_text != "Cancel" else colors["crimson_red"]
        btn_command = print_receipt if btn_text != "Cancel" else cancel_order
        btn = ctk.CTkButton(bottom_frame, text=btn_text, width=80, height=30, fg_color=color, text_color="white", command=btn_command)
        btn.pack(side="left", padx=5)


    def get_user_picture_path(username):
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT img FROM users WHERE user_name = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            if result and result[0]:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Error retrieving user picture path: {e}")
            return None

    # Load and display the user's picture
    user_picture_path = get_user_picture_path(username)
    # print("22222222222222",user_picture_path)
    if user_picture_path:
        try:
            # user_image = Image.open("./db/user.jpg")
            user_image = Image.open(user_picture_path)
            user_image = user_image.resize((350, 300), Image.ANTIALIAS)
            user_photo = ImageTk.PhotoImage(user_image)
            user_image_label = ctk.CTkLabel(main_frame, image=user_photo, text="")
            user_image_label.grid(row=0, column=2, padx=40, pady=40)
        except Exception as e:
            print(f"Error loading user picture: {e}")
    # Run the application
    # parent.destroy()

    app.mainloop()

# Example usage:
if __name__ == "__main__":
    initialize_seller_page("YourUsername",ctk.CTk(),ctk.CTk())