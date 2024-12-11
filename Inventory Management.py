import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
from datetime import datetime


# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1987nitesh",  # MySQL root password
        database="inventory_db"
    )


# Authentication with plain text password
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and password == user[2]:  # Assuming password is stored as plain text
        return user
    return None


# Inventory Management System Class
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.build_login_screen()

    def build_login_screen(self):
        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if authenticate_user(username, password):
            messagebox.showinfo("Success", "Login successful!")
            self.open_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def open_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()  # Clear the screen
        self.build_dashboard()

    def build_dashboard(self):
        # Dashboard layout
        tk.Label(self.root, text="Add Product", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)

        tk.Label(self.root, text="Name:").grid(row=1, column=0, sticky=tk.W)
        tk.Label(self.root, text="Quantity:").grid(row=2, column=0, sticky=tk.W)
        tk.Label(self.root, text="Price:").grid(row=3, column=0, sticky=tk.W)

        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=1, column=1)
        self.quantity_entry = tk.Entry(self.root)
        self.quantity_entry.grid(row=2, column=1)
        self.price_entry = tk.Entry(self.root)
        self.price_entry.grid(row=3, column=1)

        tk.Button(self.root, text="Add Product", command=self.add_product_gui).grid(row=4, columnspan=2, pady=10)

        # Inventory display
        tk.Label(self.root, text="Inventory", font=("Arial", 16)).grid(row=5, columnspan=2, pady=10)
        columns = ("ID", "Name", "Quantity", "Price", "Actions")  # Define columns, actions as the last column
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.grid(row=6, columnspan=2, pady=10)

        self.tree.bind("<ButtonRelease-1>", self.on_item_click)  # Binding to detect clicks

        tk.Button(self.root, text="Refresh Inventory", command=self.refresh_inventory).grid(row=7, columnspan=2,
                                                                                            pady=10)

        # Sales Summary
        tk.Button(self.root, text="Sales Summary", command=self.view_sales_summary).grid(row=8, columnspan=2, pady=10)

        # Low Stock Alerts
        tk.Button(self.root, text="Low Stock Alerts", command=self.generate_low_stock_alerts).grid(row=9, columnspan=2,
                                                                                                   pady=10)

    def add_product_gui(self):
        name = self.name_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()

        if name and quantity.isdigit() and price.replace('.', '', 1).isdigit():
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (name, quantity, price) VALUES (%s, %s, %s)",
                (name, int(quantity), float(price))
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Product added successfully!")
            self.name_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.refresh_inventory()
        else:
            messagebox.showerror("Error", "Invalid input. Please check your entries.")

    def refresh_inventory(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        for product in cursor.fetchall():
            product_id = product[0]  # Assuming the first column is the product ID
            # Insert the product data, but only include "Actions" in the last column
            self.tree.insert("", tk.END, values=(product[0], product[1], product[2], product[3], "Edit | Delete"),
                             tags=(product_id,))
        conn.close()

    def on_item_click(self, event):
        item = self.tree.selection()[0]  # Get the selected item
        product_id = self.tree.item(item, "tags")[0]  # Get product ID from tags

        # Check if clicked on the 'Edit' or 'Delete' column
        column = self.tree.identify_column(event.x)
        if column == "#5":  # Actions column, where buttons are displayed
            self.show_edit_delete_buttons(item, product_id)

    def show_edit_delete_buttons(self, item, product_id):
        # Display Edit and Delete options
        action = messagebox.askquestion("Actions", "Do you want to Edit the product?", icon='question')

        if action == 'yes':  # User chooses to edit
            self.edit_product(product_id)
        elif action == 'no':  # User chooses to delete
            self.delete_product(product_id)

    def edit_product(self, product_id):
        # Fetch product data and open a window to edit product
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        conn.close()

        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Product")

        tk.Label(self.edit_window, text="Name:").grid(row=0, column=0)
        tk.Label(self.edit_window, text="Quantity:").grid(row=1, column=0)
        tk.Label(self.edit_window, text="Price:").grid(row=2, column=0)

        self.edit_name = tk.Entry(self.edit_window)
        self.edit_name.grid(row=0, column=1)
        self.edit_quantity = tk.Entry(self.edit_window)
        self.edit_quantity.grid(row=1, column=1)
        self.edit_price = tk.Entry(self.edit_window)
        self.edit_price.grid(row=2, column=1)

        self.edit_name.insert(0, product[1])
        self.edit_quantity.insert(0, product[2])
        self.edit_price.insert(0, product[3])

        tk.Button(self.edit_window, text="Save", command=lambda: self.save_edits(product[0])).grid(row=3, columnspan=2)

    def save_edits(self, product_id):
        name = self.edit_name.get()
        quantity = self.edit_quantity.get()
        price = self.edit_price.get()

        if name and quantity.isdigit() and price.replace('.', '', 1).isdigit():
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE products SET name = %s, quantity = %s, price = %s WHERE id = %s",
                (name, int(quantity), float(price), product_id)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Product updated successfully!")
            self.edit_window.destroy()
            self.refresh_inventory()
        else:
            messagebox.showerror("Error", "Invalid input. Please check your entries.")

    def delete_product(self, product_id):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this product?")
        if confirm:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Product deleted successfully!")
            self.refresh_inventory()

    def view_sales_summary(self):
        start_date = "2024-01-01"  # Replace with actual logic for date selection
        end_date = datetime.now().strftime("%Y-%m-%d")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total) FROM sales WHERE date >= %s AND date <= %s", (start_date, end_date))
        sales_total = cursor.fetchone()[0]
        conn.close()

        if sales_total:
            messagebox.showinfo("Sales Report", f"Total sales from {start_date} to {end_date}: ₹{sales_total}")
        else:
            messagebox.showinfo("Sales Report", "No sales during this period.")

    def generate_low_stock_alerts(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE quantity < 5")
        low_stock_products = cursor.fetchall()
        conn.close()

        if low_stock_products:
            messagebox.showwarning("Low Stock Alerts", "The following products are low in stock:\n" +
                                   "\n".join([f"{product[1]}: {product[2]}" for product in low_stock_products]))
        else:
            messagebox.showinfo("Low Stock Alerts", "All products are sufficiently stocked.")


# Main Program
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
