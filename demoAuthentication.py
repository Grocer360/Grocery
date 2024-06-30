import customtkinter as customtkinter
from tkinter import messagebox
from PIL import Image

class Grocer360Authenticator:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocer360 Authentication")
        self.root.geometry("800x700")
        
        customtkinter.set_appearance_mode("Light")
        customtkinter.set_default_color_theme("blue")
        
        self.users = {
            "manager": {"password": "managerpass", "role": "manager"},
            "employee1": {"password": "employeepass1", "role": "employee"},
            "employee2": {"password": "employeepass2", "role": "employee"}
        }
        
        self.load_images("Picture1.png", "Picture1.png")
        
        self.mode_switch = customtkinter.CTkSwitch(root, text="Dark Mode", command=self.toggle_mode)
        self.mode_switch.pack(pady=10)
        
        self.username_label = customtkinter.CTkLabel(root, text="Username")
        self.username_label.pack(pady=5)
        self.username_entry = customtkinter.CTkEntry(root)
        self.username_entry.pack(pady=5)
        
        self.password_label = customtkinter.CTkLabel(root, text="Password")
        self.password_label.pack(pady=5)
        self.password_entry = customtkinter.CTkEntry(root, show='*')
        self.password_entry.pack(pady=5)
        
        self.login_button = customtkinter.CTkButton(root, text="Login", command=self.login)
        self.login_button.pack(pady=20)
    
    def load_images(self, light_image_path, dark_image_path):
        try:
            self.my_image = customtkinter.CTkImage(light_image=Image.open(light_image_path),
                                                   dark_image=Image.open(dark_image_path),
                                                   size=(300, 300))
            self.image_label = customtkinter.CTkLabel(self.root, image=self.my_image, text="")
            self.image_label.pack(pady=0)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def toggle_mode(self):
        if self.mode_switch.get() == 1:
            customtkinter.set_appearance_mode("Dark")
        else:
            customtkinter.set_appearance_mode("Light")
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username in self.users and self.users[username]["password"] == password:
            role = self.users[username]["role"]
            if role == "manager":
                self.manager_dashboard()
            else:
                self.employee_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def manager_dashboard(self):
        self.clear_screen()
        customtkinter.CTkLabel(self.root, text="Manager Dashboard", font=("Helvetica", 20)).pack(pady=20)
        self.create_dashboard_buttons([("Add Employee", self.add_employee), ("View Employees", self.view_employees)])
    
    def employee_dashboard(self):
        self.clear_screen()
        customtkinter.CTkLabel(self.root, text="Employee Dashboard", font=("Helvetica", 20)).pack(pady=20)
        self.create_dashboard_buttons([("Logout", self.logout)])
    
    def create_dashboard_buttons(self, buttons):
        for text, command in buttons:
            customtkinter.CTkButton(self.root, text=text, command=command).pack(pady=10)
    
    def add_employee(self):
        messagebox.showinfo("Add Employee", "Functionality to add new employee will be implemented soon!")
    
    def view_employees(self):
        messagebox.showinfo("View Employees", "Functionality to view employees will be implemented soon!")
    
    def logout(self):
        self.clear_screen()
        self.__init__(self.root)
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            if widget != self.image_label:
                widget.destroy()

if __name__ == "__main__":
    root = customtkinter.CTk()
    app = Grocer360Authenticator(root)
    root.mainloop()
