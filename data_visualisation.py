import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

class DataVisualisation(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Load the CSV file into a DataFrame
        df = pd.read_csv('./fake_data.csv')  # Adjust the path if necessary

        # Most selling category and the lowest (pie chart)
        category_sales = df.groupby('Category')['Quantity'].sum()
        
        # Each employee's total sales (bar chart)
        employee_sales = df.groupby('Employee')['Total'].sum()
        
        # Total sales per day (line chart)
        daily_sales = df.groupby('Date')['Total'].sum()
        
        # Fourth graph: Average quantity sold per category (bar chart)
        category_sales_total = df.groupby('Category')['Total'].sum()

        # Create a figure for plotting
        fig, axs = plt.subplots(4, 1, figsize=(8, 16))  # Adjusted size

        # Plot 1: Most selling category and the lowest (pie chart)
        category_sales.plot.pie(ax=axs[0], autopct='%1.1f%%')
        axs[0].set_ylabel('')
        axs[0].set_title('Most and Least Selling Categories', fontdict={'fontsize': 12, 'fontweight': 'bold', 'color': 'black'})
        
        # Plot 2: Total sales over time (line chart)
        daily_sales.plot(ax=axs[1], kind='line', marker='o')
        axs[1].set_xlabel('Date')
        axs[1].set_ylabel('Total Sales')
        axs[1].set_title('Total Sales Over Time', fontdict={'fontsize': 12, 'fontweight': 'bold', 'color': 'black'})
        axs[1].tick_params(axis='x', rotation=45)
        
        # Plot 3: Each employee's total sales (bar chart)
        employee_sales.plot.bar(ax=axs[2], color=['blue', 'green', 'yellow'])
        axs[2].set_xlabel('Employee')
        axs[2].set_ylabel('Total Sales')
        axs[2].set_title('Total Sales per Employee', fontdict={'fontsize': 12, 'fontweight': 'bold', 'color': 'black'})

        # Plot 4: Total sales by category (bar chart)
        category_sales_total.plot.bar(ax=axs[3], color=['#1f77b4', '#ff7f0e', '#2ca02c', "#d62728", '#9467bd'])
        axs[3].set_xlabel('Category')
        axs[3].set_ylabel('Total Sales')
        axs[3].set_title('Total Sales by Category', fontdict={'fontsize': 12, 'fontweight': 'bold', 'color': 'black'})

        plt.tight_layout()

        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
