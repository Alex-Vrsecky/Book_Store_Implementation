# database.py
import sqlite3
import os

class Database:
    def __init__(self, db_name="TFB.db"):
        self.db_name = db_name
        # if not os.path.exists(self.db_name):
        #     print(f"Warning: '{self.db_name}' not found. Run 'python seed_db.py'")

    def _get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def get_user(self, username):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, hash, role FROM users WHERE username = ?", [username]) # SQLite requires tuple :(
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            return {"username": user_row["username"], "hash": user_row["hash"], "role": user_row["role"]}
        return None

    def get_all_books(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return books
   
   # !!TODO extra book stuff 
    # def get_book_by_isbn(self, isbn):
    #     conn = self._get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT * FROM books WHERE isbn = ?", [isbn])
    #     row = cursor.fetchone()
    #     conn.close()
    #     return dict(row) if row else None

    # def insert_book(self, isbn, title, author, price, stock):
    #     conn = self._get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?)", (isbn, title, author, price, stock))
    #     conn.commit()
    #     conn.close()

    # def update_stock_level(self, isbn, stock):
    #     conn = self._get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute("UPDATE books SET stock = ? WHERE isbn = ?", (stock, isbn))
    #     conn.commit()
    #     conn.close()

    # def create_backorder_record(self, username, isbn, timestamp):
    #     conn = self._get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute('''
    #         CREATE TABLE IF NOT EXISTS book_requests (
    #             username TEXT, isbn TEXT, request_date TEXT
    #         )''')
    #     cursor.execute("INSERT INTO book_requests VALUES (?, ?, ?)", (username, isbn, timestamp))
    #     conn.commit()
    #     conn.close()