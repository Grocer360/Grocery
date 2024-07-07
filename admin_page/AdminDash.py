import customtkinter as ctk
import tkinter as tk

from add_product_page import AddProductPage
from view_product_page import ViewProductPage
from search_product_page import SearchProductPage
from add_employee_page import AddEmployeePage

class AdminPage(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Admin Dashboard")
        self.geometry("800x600")
        
        # Create a sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200)
        self.sidebar_frame.pack(side="left", fill="y")
        
        # Add buttons to the sidebar
        self.add_product_button = ctk.CTkButton(self.sidebar_frame, text="Add Products", command=self.show_add_product)
        self.add_product_button.pack(pady=10)
        
        self.view_product_button = ctk.CTkButton(self.sidebar_frame, text="View Products", command=self.show_view_product)
        self.view_product_button.pack(pady=10)
        
        self.search_product_button = ctk.CTkButton(self.sidebar_frame, text="Search Product", command=self.show_search_product)
        self.search_product_button.pack(pady=10)
        
        self.add_employee_button = ctk.CTkButton(self.sidebar_frame, text="Add Employees", command=self.show_add_employee)
        self.add_employee_button.pack(pady=10)
        
        # Create a main content frame
        self.main_content_frame = ctk.CTkFrame(self)
        self.main_content_frame.pack(side="right", fill="both", expand=True)
        
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

    def clear_main_content(self):
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
    
    def show_add_product(self):
        self.clear_main_content()
        add_product_page = AddProductPage(self.main_content_frame)
        add_product_page.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
    def show_view_product(self):
        self.clear_main_content()
        view_product_page = ViewProductPage(self.main_content_frame)
        view_product_page.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
    def show_search_product(self):
        self.clear_main_content()
        search_product_page = SearchProductPage(self.main_content_frame)
        search_product_page.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
    def show_add_employee(self):
        self.clear_main_content()
        add_employee_page = AddEmployeePage(self.main_content_frame)
        add_employee_page.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

if __name__ == "__main__":
    app = AdminPage()
    app.mainloop()


