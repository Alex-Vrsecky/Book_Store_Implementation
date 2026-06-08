# models.py

import os
import hashlib
import secrets
import jwt 
import datetime
import random 

class LoginController:
    def __init__(self, database, key):
        self.db = database
        self.shared_key = key
    
    # uses the salt from the db to recalculate the hash from the user's input and 
    # compare to the one in the db
    def check_password(self, plaintext, o_cipher):
        o_salt = bytes.fromhex(o_cipher[:64])
        o_hash = bytes.fromhex(o_cipher[64:])
        n_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plaintext.encode("utf-8"),
            o_salt,
            150000
        )
        return secrets.compare_digest(n_hash, o_hash)
       
    # creates a token if user's password was correct, otherwise returns None
    def validate_credentials(self, username, password):
        if not username or not password:
            return None
        
        user_record = self.db.get_user(username)
        if user_record:
            if self.check_password(password, user_record["hash"]):
                token_data = {
                    "username": user_record["username"],
                    "role": user_record["role"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                }
                
                secure_token = jwt.encode(token_data, self.shared_key, algorithm="HS256")
            
                return {
                    "username": user_record["username"],
                    "role": user_record["role"],
                    "token": secure_token
                }
        return None
    
    # called by other pages for LoginController to deconstruct the token
    # the username and role are returned for callers if it's still valid
    def verify_session_token(self, token):
        try:
            payload = jwt.decode(token, self.shared_key, algorithms=["HS256"])
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
        
    # this method is for a signup feature we probably won't implement  
    # you can also use this function independantly to create hashes from passwords
    # def hash_new_password(self, pwd):
    #     salt = os.urandom(32)
    #     hash = hashlib.pbkdf2_hmac(
    #         "sha256",
    #         pwd.encode("utf-8"),
    #         salt,
    #         150000
    #     )
    #     return salt.hex() + hash.hex()
        

# CATALOGUE CONTROLLER
class CatalogueController:
    def __init__(self, database, key):
        self.db = database
        self.shared_key = key

    # gets books from db
    def get_all_books(self):
       return self.db.get_all_books()
    
    # gets books by ISBN from db
    def get_book_by_isbn(self, isbn):
        if not isbn:
            return None
        return self.db.get_book_by_isbn(isbn)
       
    # base catalogue ui book population based on filters
    def browse_and_filter(self, search_query=None, author_filter=None):
        all_books = self.get_all_books() # Interaction with Database boundary
        
        filtered_catalogue = []
        for book in all_books:
            # Match search text if provided
            if search_query and search_query.lower() not in book['title'].lower():
                continue
            # Match author filter if provided
            if author_filter and author_filter.lower() not in book['author'].lower():
                continue
            filtered_catalogue.append(book)
            
        return {"success": True, "data": filtered_catalogue}
    
    # Checkes if token is assigned to Administrator (staff)
    def verification_of_admin(self, token, required_role):
        try: 
            payload = jwt.decode(token, self.shared_key, algorithms=["HS256"])
            if payload.get("role") == required_role:
                return {"valid": True, "username": payload.get("username")}
            return {"valid": False, "error": "Permission Denied: Limited Access."}
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return {"valid": False, "error": "Authentication Error: Invalid or Expired Session Token."}
    
    # Publishes an existing inventory item to the catalogue for customers view
    def add_new_book(self, token, isbn, title, initial_stock):
        # check if admin
        auth = self.verification_of_admin(token, "Administrator") # Checks accessibility
        if not auth["valid"]:
            return {"success": False, "error": auth["error"]}

        if self.db.get_book_by_isbn(isbn): # Ensure it is not already published
            return {"success": False, "error": "Book is already in catalogue."}
        
        inv = self.db.get_inventory_record(isbn) # Ensure the book exists in inventory stock table
        if not inv:
            return {"success": False, "error": "Book not found in inventory."}
        
        
        
        stock_val = int(initial_stock)    # Converting input to integer

        if stock_val > inv["stock"]:
            return {
                "success": False,
                "error": f"Insufficient inventory. Only {inv['stock']} units available."
            }
        
        self.db.insert_new_book(isbn, inv, stock_val) # Creates new record of book to catalogue
        self.db.update_inventory_publish_status(isbn, inv["stock"] - stock_val) # Reduces the inventory stock level of a book when published by same amount

        return {"success": True, "message": f"Successfully published '{title}'."}
    
    # Updates stock for books already in the catalogue
    def update_catalogue_stock(self, token, isbn, amount, operation):
        auth = self.verification_of_admin(token, "Administrator") # Checks accessibility
        if not auth["valid"]:
            return {"success": False, "error": auth["error"]}      

        current_book = self.db.get_book_by_isbn(isbn) # Checks if the book is in the catalogue
        if not current_book:
            return {"success": False, "error": "Book not found in catalogue. Please use 'Publish' instead."}
        
        inv = self.db.get_inventory_record(isbn) # Gets current inventory status
        amount = int(amount) 

        if operation == "add":  # Adding stock to current book in catalogue 

            if amount > inv["stock"]:
                return {
                    "success": False,
                    "error": f"Insufficient inventory. Only {inv['stock']} units available to add"
                }
            
            new_book_stock = current_book["stock"] + amount # adding new stock to the current book stock in catalogue
            new_inv_stock = inv["stock"] - amount # inventory stock reduced by same amount added into catalogue
        else: # Removing stock from book in catalogue

            if amount > current_book["stock"]:
                return {"success": False, "error": f"Cannot remove more than what is in the catalogue ({current_book['stock']} units)."}
            
            new_book_stock = max(0, current_book["stock"] - amount) # book stock is decreased, ensures cannot remove more stocks than what is currently in stock
            new_inv_stock = inv["stock"] + amount # inventory stock increased by same amount as it returns to inventory 

        self.db.update_book_stock(isbn, new_book_stock) # Saves new book stock
        self.db.update_inventory_stock(isbn, new_inv_stock) # Saves new inventory stock

        return {"success": True, "message": "Catalogue stock updated."}
    
    def get_inventory_report(self): # Retrieves all inventory stocks from the database
        return self.db.get_all_inventory_stock()


# ORDER CONTROLLER - Handles order management, payments, cart managemet, invoice and shipment
class OrderController:
    def __init__(self, database):
        self.db = database #access database for cart operations

    def get_cart_items(self,username):
        return self.db.get_cart_items(username) # returns cart items for user
    
    def add_to_cart(self, username, isbn, quantity=1):
        if not username or not isbn:
            return {"success": False, "error": "Invalid cart request."}
        
        cart_items = self.get_cart_items(username)      # Checks if item is already in cart
        if any(item['isbn'] == isbn for item in cart_items):
            msg = f"Item {isbn} is already in your cart."
            print(f"[CART IGNORED]: {msg}")
            return {"success": False, "message": msg}
        
            # requires username and ibn
        self.db.add_to_cart(username, isbn, quantity) # adds book to user's cart
        msg = f"Successfully added {isbn} to cart."
        
        print(f"[CART SUCCESS]: {msg}")
        return {"success": True, "message": msg} # alerts cart addition has been completed
    
    def update_cart_item(self, username, isbn, quantity): # Updating quantity or removing item from cart
        if not username or not isbn:
            return {"success": False, "error": "Invalid cart update."}

        try: 
            quantity = int(quantity)
        except (TypeError, ValueError):
            print(f"[CART ERROR]: Invalid quantity format: {quantity}")
            return {"success": False, "error": "Quantity must be number"} # Already handled in HTML (controlview)

        if quantity == 0:                               # Removes cart-item from the cart entirely if 0 quantity is selected
            self.db.delete_cart_item(username, isbn)
            msg = f"Item {isbn} removed from cart."
        else: 
            book = self.db.get_book_by_isbn(isbn)

            if quantity > book["stock"]:
                print(f"[CART ERROR]: Stock limit exceeded. Requested: {quantity}")
                return {"success": False, "error": "Not enough stock available."} # ensures requested quantity does not exceed the stock amount

            self.db.update_cart_quantity(username, isbn, quantity) # updates the quantity of items in cart
            msg = f"Quantity updated for {isbn} to {quantity}."

        print(f"[CART SUCCESS]: {msg}")
        return {"success": True, "message": msg}
    
    def clear_cart(self, username): 
        if not username:
            return{"success": False, "error": "Invalid request"} #requires username
        self.db.clear_cart(username) # removes all items in cart
        return {"success": True}

    def get_invoice_details(self, username):        # Calculates cart total
        """Gathering information for Invoice"""
        items = self.get_cart_items(username) # fetch user's cart
        if not items:
            return None
    
        total = sum(item["price"] * item["quantity"] for item in items)

        return {
            "items": items,
            "total": total
        }
    
    # For app.py
    def get_all_orders(self):   
        return self.db.get_all_orders()
    def update_order_status(self, order_num, new_status):
        return self.db.update_order_status(order_num, new_status)
    def get_orders_by_username(self, username):
        return self.db.get_orders_by_username(username)
    def get_order_by_num(self, order_num):
        return self.db.get_order_by_num(order_num)
    def get_order_items(self, order_num):
        return self.db.get_order_items(order_num)
    
    def process_customer_order(self, username, card_details, delivery_address, total): #Finalizes transaction and updates stock records in catalogue/catalogue management
        # Checks if credit card is 16 digits
        card_number = card_details["card_number"]
        if not (card_number.isdigit() and len(card_number) == 16):
            return False, "Payment Failed. Check Card Details, Your card number was not 16 digits."


        cart_items = self.get_cart_items(username) # Ensures cart is not empty
        if not cart_items:
            return False, "Cart is empty."
        
        drivers = self.db.get_drivers_by_courier("FedEx") # Assigns a random driver from the courier service FedEx
        if drivers:
            chosen_driver = random.choice(drivers)
            d_name = chosen_driver['name']
            d_phone = chosen_driver['delivery_person_phone']
        else: 
            d_name = "Unassigned"
            d_phone = "N/A"
        
        # Prepares order data
        order_num = f"Order#{random.randint(1000, 9999)}" # Once placed, customers receive a random 4 digit order number e.g. Order#1394
        order_data = {
            "order_num": order_num,
            "username": username,
            "address": delivery_address,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "courier": "FedEx",
            "d_name": d_name,
            "d_phone": d_phone,
            "status": "Processed"
        }

        self.db.record_order(order_data, cart_items) # Saves order to DB

        for item in cart_items:

            self.db.deduct_stock_after_purchase(item['isbn'], item['quantity']) # Removes stock from main catalogue shock based on order items

        self.db.clear_cart(username) # Clears customers cart after payment and processed

        return True, f"Payment of ${total:.2f} was successful! Your order number is {order_num}."

        
    
        

        