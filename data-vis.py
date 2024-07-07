# import numpy as np # linear algebra
# import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# # ---- imported libaray ---------
# import matplotlib.pyplot as plt
# import seaborn as sns
# #--------------------------------



# df = pd.read_csv('grocery_store_sales_large.csv')
# df['date'] = pd.to_datetime(df['date'])
# # --------------------------------------------------------------------------------
# summary_stats = df.describe()
# # print(summary_stats)
# # --------------------------------------------------------------------------------
# total_sales_per_cashier = df.groupby('cashier_name')['total_transaction'].sum()
# total_sales_per_cashier["employee_1"] = total_sales_per_cashier["employee_1"] * 2
# total_sales_per_cashier["employee_2"] = total_sales_per_cashier["employee_1"] * 5
# total_sales_per_cashier["employee_3"] = total_sales_per_cashier["employee_1"] * 3
# print(total_sales_per_cashier)
# # --------------------------------------------------------------------------------
# sales_over_time = df.groupby('date')['total_transaction'].sum()
# # print(sales_over_time)
# # --------------------------------------------------------------------------------
# sales_percentage_by_cashier = total_sales_per_cashier / total_sales_per_cashier.sum() * 100
# # print(sales_percentage_by_cashier)
# # --------------------------------------------------------------------------------
# sales_frequency = df.pivot_table(index='date', columns='cashier_name', values='total_transaction', aggfunc='count', fill_value=0)
# # print(sales_frequency)
# # --------------------------------------------------------------------------------
# plt.figure(figsize=(8, 8))
# # Get the figure manager
# manager = plt.get_current_fig_manager()

# # For the TkAgg backend, you can maximize the window
# manager.window.state('zoomed')
# # Bar chart: Total sales per cashier

# plt.subplot(2, 2, 1)
# total_sales_per_cashier.plot(kind='bar', color=['blue', 'green', 'yellow'])
# plt.title('Total Sales per Cashier',fontdict={'fontsize': 16, 'fontweight': 'bold', 'color': 'black'})
# plt.xlabel('Cashier Name')
# plt.ylabel('Total Sales')

# # Line chart: Sales over time


# plt.subplot(2, 2, 2)
# sales_over_time.plot(kind='line', marker='o')
# plt.title('Total Sales Over Time',fontdict={'fontsize': 16, 'fontweight': 'bold', 'color': 'black'})
# plt.xlabel('Date')
# plt.ylabel('Total Sales')

# # Pie chart: Percentage of total sales by cashier

# plt.subplot(2, 2, 3)
# sales_percentage_by_cashier.plot(kind='pie', autopct='%1.1f%%', colors=['blue', 'green', 'yellow'])

# plt.title('Percentage of Total Sales by Cashier',
#           fontdict={'fontsize': 16, 'fontweight': 'bold', 'color': 'black'},)



# plt.tight_layout()
# plt.subplots_adjust(left=0.08, right=0.97, top=0.945, bottom=0, wspace=0.305, hspace=0.69)
# plt.show()
# # --------------------------------------------------------------------------------
# # --------------------------------------------------------------------------------
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# ---- imported libaray ---------
import matplotlib.pyplot as plt
import seaborn as sns
#--------------------------------

class DataVisualisation():
  def __init__(self):

    df = pd.read_csv('grocery_store_sales_large.csv')
    df['date'] = pd.to_datetime(df['date'])
    # --------------------------------------------------------------------------------
    summary_stats = df.describe()
    # print(summary_stats)
    # --------------------------------------------------------------------------------
    total_sales_per_cashier = df.groupby('cashier_name')['total_transaction'].sum()
    total_sales_per_cashier["employee_1"] = total_sales_per_cashier["employee_1"] * 2
    total_sales_per_cashier["employee_2"] = total_sales_per_cashier["employee_1"] * 5
    total_sales_per_cashier["employee_3"] = total_sales_per_cashier["employee_1"] * 3
    print(total_sales_per_cashier)
    # --------------------------------------------------------------------------------
    sales_over_time = df.groupby('date')['total_transaction'].sum()
    # print(sales_over_time)
    # --------------------------------------------------------------------------------
    sales_percentage_by_cashier = total_sales_per_cashier / total_sales_per_cashier.sum() * 100
    # print(sales_percentage_by_cashier)
    # --------------------------------------------------------------------------------
    sales_frequency = df.pivot_table(index='date', columns='cashier_name', values='total_transaction', aggfunc='count', fill_value=0)
    # print(sales_frequency)
    # --------------------------------------------------------------------------------
    plt.figure(figsize=(8, 8))
    # Get the figure manager
    manager = plt.get_current_fig_manager()

    # For the TkAgg backend, you can maximize the window
    manager.window.state('zoomed')
    # Bar chart: Total sales per cashier

    plt.subplot(2, 2, 1)
    total_sales_per_cashier.plot(kind='bar', color=['blue', 'green', 'yellow'])
    plt.title('Total Sales per Cashier',fontdict={'fontsize': 16, 'fontweight': 'bold', 'color': 'black'})
    plt.xlabel('Cashier Name')
    plt.ylabel('Total Sales')

    # Line chart: Sales over time


    plt.subplot(2, 2, 2)
    sales_over_time.plot(kind='line', marker='o')
    plt.title('Total Sales Over Time',fontdict={'fontsize': 16, 'fontweight': 'bold', 'color': 'black'})
    plt.xlabel('Date')
    plt.ylabel('Total Sales')

    # Pie chart: Percentage of total sales by cashier

    plt.subplot(2, 2, 3)
    sales_percentage_by_cashier.plot(kind='pie', autopct='%1.1f%%', colors=['blue', 'green', 'yellow'])

    plt.title('Percentage of Total Sales by Cashier',
              fontdict={'fontsize': 16, 'fontweight': 'bold', 'color': 'black'},)



    plt.tight_layout()
    plt.subplots_adjust(left=0.08, right=0.97, top=0.945, bottom=0, wspace=0.305, hspace=0.69)
    plt.show()
    


DataVisualisation()
