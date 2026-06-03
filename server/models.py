# models.py

import os
import hashlib
import secrets
import jwt 
import datetime

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

    # # STAFF CATALOGUE MANAGEMENT BOUNDARIES - NOT FINISHED!!
    # The /catalogue page behaves differently when an admin session token visits
    # allows catalogue editing
    # def add_new_book(self, token, isbn, title, author, price, initial_stock):

    #     # check if admin
    #     auth = self._verify_role_permission(token, "Administrator")
    #     if not auth["valid"]:
    #         return {"success": False, "error": auth["error"]}

    #     # input Validation handling
    #     if not isbn or len(isbn.replace("-", "")) != 13:
    #         return {"success": False, "error": "Invalid Input: ISBN must be a valid 13-digit sequence."}
    #     if not title or not author:
    #         return {"success": False, "error": "Invalid Input: Title and Author fields cannot be blank."}
    #     try:
    #         price_val = float(price)
    #         stock_val = int(initial_stock)
    #         if price_val < 0 or stock_val < 0:
    #             raise ValueError()
    #     except ValueError:
    #         return {"success": False, "error": "Invalid Input: Price and Stock metrics must be non-negative numeric values."}

    #     # check for book duplicates
    #     existing_book = self.db.get_book_by_isbn(isbn)
    #     if existing_book:
    #         return {"success": False, "error": f"Collision Error: A record for ISBN {isbn} already exists."}

    #     # commit changes via database object
    #     self.db.insert_book(isbn, title, author, price_val, stock_val)
    #     return {"success": True, "message": f"Successfully registered '{title}' to the active catalogue."}


    # # MANUAL STAFF STOCK UPDATE 
    # def update_inventory_stock(self, token, isbn, new_stock_count):
    #     auth = self._verify_role_permission(token, "Administrator")
    #     if not auth["valid"]:
    #         return {"success": False, "error": auth["error"]}      
    #     try:
    #         stock_val = int(new_stock_count)
    #         if stock_val < 0:
    #             raise ValueError()
    #     except ValueError:
    #         return {"success": False, "error": "Processing Error: Inventory units must be an integer zero or greater."}

       
    #     target_book = self.db.get_book_by_isbn(isbn)
    #     if not target_book:
    #         return {"success": False, "error": "Query Error: Target ISBN does not exist in inventory catalog."}

    #     self.db.update_stock_level(isbn, stock_val)
    #     return {"success": True, "message": f"Updated '{target_book['title']}' stock matrix to {stock_val} units."}

    # # NO STOCK HANDLING
    # def register_out_of_stock_request(self, username, isbn):
    #     target_book = self.db.get_book_by_isbn(isbn)
    #     if not target_book:
    #         return {"success": False, "error": "Invalid target book sequence."}
            
    #     if target_book['stock'] > 0:
    #         return {"success": False, "error": "Validation Error: Item is currently in stock; proceed to direct checkout."}

    #     self.db.create_backorder_record(username, isbn, timestamp=datetime.now().isoformat())
    #     return {"success": True, "message": "Backorder request logged successfully. Staff will review shortly."}