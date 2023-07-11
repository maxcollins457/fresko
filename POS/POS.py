import tkinter as tk
from tkinter import messagebox
import psycopg2
from collections import Counter
from tkinter import ttk

# Connect to the PostgreSQL database
def connect_to_database():
    '''
    Connects to postgreSQL database
    
    If unsuccessful, resturns the error recieved
    '''
    try:
        connection = psycopg2.connect(
            host="127.0.0.1",
            database="DB_NAME_HERE",
            user="YOUR_USER_HERE", #Remember to change these details
            password="YOUR_PASSWORD HERE"
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Database Connection Error", str(error))
        return None

class WelcomeWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POS System")
        self.geometry('1050x600+0+0')
        
        label_title = tk.Label(self, text="Welcome to the POS System!")
        label_title.pack(padx=10, pady=10)

        button_start = tk.Button(self, text="Sign In", command=self.open_sign_in)
        button_start.pack(padx=10, pady=5)


        button_exit = tk.Button(self, text="Exit", command=self.destroy)
        button_exit.pack(padx=10, pady=5)
    
    def open_sign_in(self):
        self.withdraw()
        SignInMenu(self)

class SignInMenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("POS System")
        self.geometry('1050x600+0+0')
        
        label_title = tk.Label(self, text="Please sign in")
        label_title.pack(padx=10, pady=10)
        
        #Username field
        label_user_id = tk.Label(self, text="User ID:")
        label_user_id.pack(padx=10, pady=5)
        self.entry_user_id = tk.Entry(self)
        self.entry_user_id.pack(padx=10, pady=5)
        
        #Password field
        label_password = tk.Label(self, text="Password:")
        label_password.pack(padx=10, pady=5)
        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack(padx=10, pady=5)
        
        #Enter
        button_enter = tk.Button(self, text="Enter", command=self.check_credentials)
        button_enter.pack(padx=10, pady=5)
        
        #Exit
        button_back = tk.Button(self, text="Back", command= self.close_submenu)
        button_back.pack(padx=10, pady=5)
    
    def check_credentials(self):
        '''
        Sign in section of the POS system
        
        User must enter password and id to enter the main menu
        '''
        user_id = self.entry_user_id.get()
        password = self.entry_password.get()
        
        #clear the entries
        self.entry_user_id.delete(0, 'end')
        self.entry_password.delete(0, 'end')
        
        
        if user_id == 'User' and password == 'pass':
            self.withdraw()
            MainMenu(self)
        else:
            messagebox.showerror("Credential Error", "Username or Password was incorrect\n\nTry again")
            
    def close_submenu(self): 
        self.destroy()  # Destroy the submenu
        self.master.deiconify()  # Show the main menu


class MainMenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("POS System")
        self.geometry('1050x600+0+0')
        
        label_title = tk.Label(self, text="Main Menu")
        label_title.pack(padx=10, pady=10)
        label_menu = tk.Label(self, text="Select an option:")
        label_menu.pack(padx=10, pady=10)
        
        #Takes user to open orders
        button_orders = tk.Button(self, text="View Orders", command=self.open_view_order_submenu)
        button_orders.pack(padx=10, pady=5)
        
        #
        button_food = tk.Button(self, text="New Order", command=self.open_new_order_submenu)
        button_food.pack(padx=10, pady=5)
        
        button_payment = tk.Button(self, text="Payment", command=self.open_payment_submenu)
        button_payment.pack(padx=10, pady=5)
        
        #
        button_stock = tk.Button(self, text="Stock Counts", command=self.open_stock_submenu)
        button_stock.pack(padx=10, pady=5)

        button_exit = tk.Button(self, text="Exit", command=self.close_submenu)
        button_exit.pack(padx=10, pady=5)

    def open_view_order_submenu(self):
        self.withdraw()  # Hide the main menu
        ViewOrderSubmenu(self)
        
    def open_new_order_submenu(self):
        self.withdraw() #Hide current menu
        NewOrderSubmenu(self)
        
    def open_stock_submenu(self):
        self.withdraw()
        StockSubmenu(self)
    
    def open_payment_submenu(self):
        self.withdraw()
        PaymentSubmenu(self)
    
    def close_submenu(self): 
        self.destroy()  # Destroy the submenu
        self.master.deiconify()  # Show the main menu


class NewOrderSubmenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("POS System")
        self.geometry('1050x600+0+0')
        
        
        #New order
        self.default_option_table = "Select a table number" # Default opion for table dropdown menu
        # The selected table will be shown as a string
        self.selected_table = tk.StringVar(self)
        #List of tables
        table_list = self.get_tables_numbers()
        self.clear_order()
        
        # Menu Items -> Get from postgreSQL database
        self.menu_ids, self.menu_names = self.get_menu_items()
        
        # Set up frame for food options
        label_menu_options = tk.Label(self, text="Menu Options")
        label_menu_options.pack(padx=10, pady=10)
        

        # Create and place the buttons in a grid layout
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(padx=10, pady=5)
        self.buttons = []
        self.create_button_grid(frame_buttons)
    
        
        
        # Create Dropdown menu for table selection
        drop = tk.OptionMenu(self , self.selected_table , *table_list )
        drop.pack(pady=40)
        
        button_confirm_order = tk.Button(self, text="Confirm order", command=self.confirm_order)
        button_confirm_order.pack(padx=10, pady=5)

        # Back button
        button_back = tk.Button(self, text="Back to Main Menu", command=self.close_submenu)
        button_back.pack(padx=10, pady=5)
        
        # Create the treeview to display the order
        self.treeview = ttk.Treeview(self, columns=("Item Name", "Item ID"))
        self.treeview.heading("#0", text="Item Name")
        self.treeview.heading("#1", text="Item ID")
        self.treeview.pack(padx=10, pady=10)
        
        # Show the order in the treeview
        self.show_order()
        
        button_clear_order = tk.Button(self, text="Clear order", command=self.clear_order)
        button_clear_order.pack(padx=10, pady=5)
        
        
    def get_menu_items(self):
        connection = connect_to_database()
        if connection is None:
            return

        try:
            # Create a cursor to interact with the database
            cursor = connection.cursor()

            # Execute the SQL query to select menu item IDs and names
            select_query = "SELECT menu_item_id, menu_item_name FROM \"MenuItem\";"
            cursor.execute(select_query)

            # Fetch all the rows returned by the query
            rows = cursor.fetchall()

            # Extract item names/ids
            menu_name, menu_id =  zip(*rows)
            
            # Close the cursor
            cursor.close()
            return list(menu_name), list(menu_id) 
        except (Exception, psycopg2.Error) as error:
            # Handle any errors that occur during the execution
            print(f"An error occurred: {str(error)}")
            connection.close()
            
            
    def get_tables_numbers(self):
        connection = connect_to_database()
        if connection is None:
            return

        try:
            # Create a cursor to interact with the database
            cursor = connection.cursor()
            
            # Execute the SQL query to select table numbers (SHOULD MAYBE BE ONLY TAKEN FROM OCCUPIED TABLES)
            select_query = "SELECT table_id FROM \"TableNumber\";"
            cursor.execute(select_query)

            # Fetch all the rows returned by the query
            rows = cursor.fetchall()
            
            # Extract as list of ints
            table_numbers = ['Table '+ str(row[0]) for row in rows]
            
            # Close the cursor
            cursor.close()
            return table_numbers
        except (Exception, psycopg2.Error) as error:
            # Handle any errors that occur during the execution
            print(f"An error occurred: {str(error)}")
            connection.close()
                

    def create_button_grid(self, frame):
        for button in self.buttons:
            button.destroy()

        self.buttons = []
        for i, item in enumerate(self.menu_names):
            button = tk.Button(frame, text=item, command=lambda i=i: self.add_to_order(self.menu_names[i], self.menu_ids[i]))
            button.grid(row=i // 2, column=i % 2, padx=5, pady=5)
            self.buttons.append(button)
            
            
    def add_to_order(self, name, item_id):        
        self.order_names.append(name)
        self.order_ids.append(item_id)
        self.show_order()  # Update the treeview with the new item
   
    def show_order(self):
        self.treeview.delete(*self.treeview.get_children())

        # Insert the items from the order into the treeview
        for name, item_id in zip(self.order_names, self.order_ids):
            self.treeview.insert("", tk.END, text=name, values=(item_id,))
        
        
    def clear_order(self):
        self.order_names = []
        self.order_ids = []
        self.selected_table.set(self.default_option_table)
        try:
            self.show_order()
        except:
            pass
        
        
    def confirm_order(self):
        if self.selected_table == self.default_option_table:
            messagebox.showerror("No Table Selected", "No Table\n\nPlease select a table")
            return
        else:
            #Convert to just id of table
            selected_table_id = self.selected_table.get().split(' ')[-1]
            
        #Check there are items to be added
        if len(self.order_ids) == 0:
            messagebox.showerror("Empty Order", "Empty order\n\nPlease add some items")
            return
        
        #Connect to databasw
        connection = connect_to_database()
        if connection is None:
            return

        try:
            cursor = connection.cursor()
            #Find ids and quantities in orders
            self.ids = []
            self.quantities = []
            for i, q in Counter(self.order_ids).items():
                self.ids.append(int(i))
                self.quantities.append(int(q))
            
            # Execute query to call function in postgres
            selected_table_id = self.selected_table.get().split(' ')[-1]
            
            select_query = f"SELECT create_new_order(ARRAY{self.ids}, ARRAY{self.quantities}, {selected_table_id});"
            cursor.execute(select_query)
            cursor.close()
            connection.commit() # Commit the transaction
            
            messagebox.showinfo("Order confirmed", f"Order has been placed on: Table {selected_table_id}.")
            #Empty the order 
            self.clear_order()

        #If query error: show it
        except (Exception, psycopg2.Error) as error:
            messagebox.showerror("Query Error", str(error))
            connection.close()
            return
        

    def close_submenu(self):
        #Empty the order 
        self.clear_order()
        self.destroy()  # Destroy the submenu
        self.master.deiconify()  # Show the main menu


class ViewOrderSubmenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("POS System")
        self.geometry('1050x600+0+0')

        # Create a tabbed layout
        tab_control = ttk.Notebook(self)
        
        open_orders_tab = ttk.Frame(tab_control)
        closed_orders_tab = ttk.Frame(tab_control)
        
        tab_control.add(open_orders_tab, text="Open Orders")
        tab_control.add(closed_orders_tab, text="Closed Orders")
        
        tab_control.pack(expand=True, fill=tk.BOTH)

        # Fetch and display open orders
        open_orders = self.fetch_orders("open")
        self.display_orders(open_orders, open_orders_tab)

        # Fetch and display closed orders
        closed_orders = self.fetch_orders("closed")
        self.display_orders(closed_orders, closed_orders_tab)
        
        # Back button
        button_back = tk.Button(self, text="Back to Main Menu", command=self.close_submenu)
        button_back.pack(padx=10, pady=5)
        

    def fetch_orders(self, status):
        self.connection = connect_to_database()
        if self.connection is None:
            return

        try:
            self.cursor = self.connection.cursor()
            
            query = f"SELECT table_id, menu_item_name, price, quantity \
                    FROM get_todays_orders() WHERE status = '{status}'"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except (Exception, psycopg2.Error) as error:
            # Handle any errors that occur during the execution
            print(f"An error occurred: {str(error)}")
            return
            

    def display_orders(self, orders, tab):
        if orders:
            self.treeview = ttk.Treeview(tab, columns=("Table Number", "Menu Item", "Price", "Quantity"))
            self.treeview.heading("#0", text="Table Number")
            self.treeview.heading("#1", text="Menu Item")
            self.treeview.heading("#2", text="Price")
            self.treeview.heading("#3", text="Quantity")

            for order in orders:
                self.treeview.insert("", tk.END, text=order[0], values=order[1:])

            self.treeview.pack(expand=True, fill=tk.BOTH)
        else:
            label_no_orders = tk.Label(tab, text="No orders found.")
            label_no_orders.pack(padx=10, pady=10)

            
    def close_submenu(self):
        # Close the database connection and destroy the submenu
        self.cursor.close()
        self.connection.close()
        self.destroy()
        self.master.deiconify()  # Show the main menu



class StockSubmenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Stock Submenu")
        self.geometry('1050x600+0+0')
        
        self.treeview = ttk.Treeview(self, columns=("Ingredient Name", "Expiry Date", "Quantity", "Units"))
        self.treeview.heading("#0", text="Ingredient ID")
        self.treeview.heading("#1", text="Ingredient Name")
        self.treeview.heading("#2", text="Expiry Date")
        self.treeview.heading("#3", text="Quantity")
        self.treeview.heading("#4", text="Units")
        self.treeview.pack(expand=True, fill=tk.BOTH)
        
        
        self.display_stock()
        
        # Back button
        button_back = tk.Button(self, text="Back to Main Menu", command=self.close_submenu)
        button_back.pack(padx=10, pady=5)

    def display_stock(self):
        self.connection = connect_to_database()
        if self.connection is None:
            return
        
        try:
            self.cursor = self.connection.cursor()
        
            query = """
                SELECT cs.ingredient_id, i.ingredient_name, cs.expiry_date, cs.quantity, cs.units
                FROM "CurrentStock" cs
                INNER JOIN "Ingredient" i ON cs.ingredient_id = i.ingredient_id
            """
            self.cursor.execute(query)
            stock_data = self.cursor.fetchall()

            for stock in stock_data:
                ingredient_id, ingredient_name, expiry_date, quantity, units = stock
                self.treeview.insert("", tk.END, text=ingredient_id, values=(ingredient_name, expiry_date, quantity, units))
        except (Exception, psycopg2.Error) as error:
            # Handle any errors that occur during the execution
            print(f"An error occurred: {str(error)}")
            return

    def close_submenu(self):
        # Close the database connection and destroy the submenu
        self.cursor.close()
        self.connection.close()
        self.destroy()
        self.master.deiconify()  # Show the main menu


class PaymentSubmenu(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Payment Submenu")
        self.geometry('1050x600+0+0')
        
        
        
        #New payment
        self.default_option_table = "Select a table number" # Default opion for table dropdown menu
        # The selected table will be shown as a string
        self.selected_table = tk.StringVar(self)
        #List of tables
        table_list = self.get_open_tables_numbers()
        # Create Dropdown menu for table selection
        drop = tk.OptionMenu(self , self.selected_table , *table_list, command = self.update_checkboxes)
        drop.pack(pady=40)
    
    
        self.checkboxes_frame = tk.Frame(self)
        self.checkboxes_frame.pack()
        

        # Create a button to calculate the total and process the payment
        button_pay = tk.Button(self, text="Pay", command=self.process_payment)
        button_pay.pack(pady=10)

        # Create a label to display the total amount
        self.label_total = tk.Label(self, text="")
        self.label_total.pack()
        
        # Back button
        button_back = tk.Button(self, text="Back to Main Menu", command=self.close_submenu)
        button_back.pack(padx=10, pady=5)
        
    def update_checkboxes(self, selected_table):
        # Clear existing checkboxes
        for checkbox in self.checkboxes_frame.winfo_children():
            checkbox.destroy()

        # Fetch the orders for the selected table
        self.orders = self.fetch_order(int(selected_table.split(" ")[-1]))

        # Create a checkbox for each menu item in the orders
        self.item_vars = []
        for item in self.orders:
            menu_item_name = item[0]  # Extract the menu item name from the fetched orders
            var = tk.IntVar()
            self.item_vars.append(var)
            checkbox = tk.Checkbutton(self.checkboxes_frame, text=menu_item_name, variable=var)
            checkbox.pack(anchor=tk.W)
        
    def get_open_tables_numbers(self):
        table_numbers = []
        self.connection = connect_to_database()
        if self.connection is None:
            return

        try:
            # Create a cursor to interact with the database
            self.cursor = self.connection.cursor()
            
            # Execute the SQL query to select table numbers where thye have open orders
            select_query = f"SELECT distinct(table_id) FROM get_todays_orders() WHERE status = 'open'"
            self.cursor.execute(select_query)

            # Fetch all the rows returned by the query
            rows = self.cursor.fetchall()
            
            # Extract as list of ints
            table_numbers = ['Table '+ str(row[0]) for row in rows]
            
            # Close the cursor
            self.cursor.close()
            return table_numbers
        except (Exception, psycopg2.Error) as error:
            # Handle any errors that occur during the execution
            print(f"An error occurred: {str(error)}")
            self.connection.close()

    def fetch_order(self, table_num):
        if not isinstance(table_num, int):
            return []
        
        self.connection = connect_to_database()
        if self.connection is None:
            return

        try:
            self.cursor = self.connection.cursor()
            
            query = f"SELECT menu_item_name, price, quantity \
                    FROM get_todays_orders() WHERE status = 'open' and table_id = {table_num}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except (Exception, psycopg2.Error) as error:
            # Handle any errors that occur during the execution
            print(f"An error occurred: {str(error)}")
            return
        
    def process_payment(self):
        # Calculate the total amount based on the selected menu items
        total = 0
        for i, var in enumerate(self.item_vars):
            if var.get() == 1:
                # Placeholder code: calculate the total based on the prices
                total += i + 1  # Assuming the prices are 1, 2, 3, 4, 5

        # Display the total amount
        self.label_total.configure(text=f"Total Amount: ${total}")

        # Process the payment (placeholder code)
        # You can add your logic here to handle the payment process
        messagebox.showinfo("Payment Processed", f"Payment of ${total} processed successfully!")

    def close_submenu(self):
        # Close the database connection and destroy the submenu
        self.cursor.close()
        self.connection.close()
        self.destroy()
        self.master.deiconify()  # Show the main menu


if __name__ == "__main__":
    window = WelcomeWindow()
    window.mainloop()
