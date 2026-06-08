# database.py
import sqlite3
import os

class Database:
    def __init__(self, db_name="TFB.db"):
        self.db_name = db_name

    def _get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    # fetch a user from db
    def get_user(self, username):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, hash, role FROM users WHERE username = ?", [username]) # SQLite requires tuple :(
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            return {"username": user_row["username"], "hash": user_row["hash"], "role": user_row["role"]}
        return None
    

# BOOK RELATED DB STATEMENTS

    # get a complete list of books
    def get_all_books(self): 
        conn = self._get_connection() #opens DB connection
        cursor = conn.cursor() # cursor creation
        cursor.execute("SELECT * FROM books") # select all book rows
        books = [dict(row) for row in cursor.fetchall()] # converts rows to dicts
        conn.close()
        return books # returns the full book list
    
    def get_book_by_isbn(self, isbn):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE isbn = ?", [isbn]) # queries book by ISBN
        row = cursor.fetchone() # retrieves matching row
        conn.close()
        return dict(row) if row else None
    
# CART RELATED DB STATEMENTS
    
    def get_cart_items(self, username): # Get all items currently in user cart
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.isbn, b.title, b.author, b.price, c.quantity, b.stock 
            FROM carts c
            JOIN books b ON c.isbn = b.isbn
            WHERE c.username = ?    
        ''', (username,)) #
        cart_items = [dict(row) for row in cursor.fetchall()] # Converting rows to dicts (for python reading)
        conn.close()
        return cart_items
    
    def add_to_cart(self, username, isbn, quantity=1): #Adding book to cart
        conn = self._get_connection()
        cursor = conn.cursor()
        # checks if cart entry already exists
        cursor.execute(
            "INSERT INTO carts (username, isbn, quantity) VALUES (?,?,?)",
            (username, isbn, quantity)
        ) #creates new cart item row if none exists
            
        conn.commit()
        conn.close()

    def update_cart_quantity(self, username, isbn, quantity): # Updating specfic item quantity in user carts
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE carts SET quantity = ? WHERE username = ? AND isbn = ?",
            (quantity, username, isbn)
        ) # updates the existing cart row regarding the quantity
        conn.commit()
        conn.close()

    def delete_cart_item(self, username, isbn):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM carts WHERE username = ? AND isbn = ?",
            (username, isbn)
        )
        conn.commit()
        conn.close()

    def clear_cart(self, username): # Clearing all items in carts for user
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM carts WHERE username = ?", (username,)) # deletes all cart item rows
        conn.commit()
        conn.close()

   # INVENTORY STOCK DB STATEMENTS (STAFF ONLY)

    def get_all_inventory_stock(self): # Retrieve full inventory report
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory") # Retrieve all items from inventory table
        stock = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return stock
    
    
    def get_book_stock(self, isbn):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM books WHERE isbn = ?", (isbn,)) # Retrieves specific stock level of a book from catalogue
        res = cursor.fetchone()
        conn.close()
        return res["stock"] if res else None
    
    def get_inventory_record(self, isbn):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE isbn = ?", (isbn,)) # Retrieves full inventory record for a book from inventory stock table
        res = cursor.fetchone()
        conn.close()
        return res
        
    
    def update_book_stock(self, isbn, new_stock):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET stock = ? WHERE isbn = ?", (new_stock, isbn)) # Updates stock count for a book in catalogue
        conn.commit()
        conn.close()

    def update_inventory_stock(self, isbn, new_stock):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET stock = ? WHERE isbn = ?", (new_stock, isbn)) # Updates stock level for a book in inventory stock table 
        conn.commit()
        conn.close()


    def insert_new_book(self, isbn, inv, stock):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""          
            INSERT INTO books (isbn, title, author, price, stock, is_published) 
            VALUES (?, ?, ?, ?, ?, True) 
        """, (isbn, inv["title"], inv["author"], inv["price"], stock)) # Moves book from inventory to catalogue table
        conn.commit()
        conn.close()

    def update_inventory_publish_status(self, isbn, new_stock): # Adjusts the status of books in inventory table (published yet) and updates stock in inventory when is added
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET is_published = True, stock = ? WHERE isbn = ?", (new_stock, isbn))
        conn.commit()
        conn.close()

# Reflection of real-time stock after order has been placed
    def deduct_stock_after_purchase(self, isbn, quantity): # Decreases stock in store catalogue (clearer from staff view) after customer order has been paid and placed
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE books SET stock = stock - ? WHERE isbn = ?''', (quantity, isbn)) # Updates the catalogue and their respective stock
        conn.commit()
        conn.close()

# ORDER DB STATEMENTS

    def record_order(self, order_data, items): # Save completed order and its details

        conn = self._get_connection()
        cursor = conn.cursor()
        # Stores the customers information, their delivery details
        cursor.execute('''
            INSERT INTO orders (order_num, username, delivery_address, date_of_order_placed, courier_name, delivery_person_name, delivery_person_phone, order_status)
            VALUES (?, ?, ?, ?, 'FedEx', ?, ?, ?)
        ''', (order_data['order_num'], order_data['username'], order_data['address'], 
              order_data['date'], order_data['d_name'], 
              order_data['d_phone'], order_data['status']))
        
        # Goes through each item in cart and saves it to the order_items table linked by the order_num (unique for every different order)
        for item in items:
            cursor.execute('''
                INSERT INTO order_items (order_num, isbn, title, author, quantity, price)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (order_data['order_num'], item['isbn'], item['title'],
                  item['author'], item['quantity'], item['price']))
        conn.commit()
        conn.close()

    def get_all_orders (self): # Retrieve all orders

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders") # Selects all rows from order table
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return orders

    def update_order_status(self, order_num, new_status): # Changing order status of order table 

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE orders 
            SET order_status = ?
            WHERE order_num = ?
        ''', (new_status, order_num))
        conn.commit()
        conn.close()

    def get_drivers_by_courier(self, courier_name): # Gets delivery driver information relative to their specific courier service (company e.g FedEx)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, delivery_person_phone
            FROM delivery_personnel
            WHERE courier_service_type = ?
        ''', (courier_name,))

        drivers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return drivers
    
    def get_orders_by_username(self, username): # Get orders for a specific user e.g john99
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE username = ?", (username,))
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return orders
    
    def get_order_items(self, order_num): # Get all items for one specific order
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM order_items WHERE order_num = ?", (order_num,))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def get_order_by_num(self, order_num): # Find one specific order (can be any user)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_num = ?", (order_num,))
        order = cursor.fetchone()
        conn.close()
        return dict(order) if order else None