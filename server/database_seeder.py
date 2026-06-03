# seed_db.py
import sqlite3
import os

# ============= RUN TO INITIALIZE A LOCAL DATABASE ================

DB_NAME = "TFB.db"

fake_data = {
    "users": [
        # the admin password is password1
        ("admin", "0e0214527b0703f0c522400032a0e55f001bb6aceedcae5974730ae65aab84844f8b668c95e65c215d8f8b3225baffe40398d401d499aca2e9f1a8de5b85a7de", "Administrator"),
        # the john99 user password is password2
        ("john99", "18a6bb4b62f15bcaa70245d5c0809a8bceb83aa8501edb78072667bc8d70fd0ce5ad06ccbe0fdc5cc1845fa4392dc0a5f51410959704c9a316c1f6c0c5ba4337", "Customer")
    ],
    "books": [
        ("978-0134092660", "Networking Essentials", "Cisco Press", 89.99, 12),
        ("978-1119642817", "CompTIA Security+ Study Guide", "Mike Chapple", 59.95, 25),
        ("978-0596009205", "Head First Design Patterns", "Eric Freeman", 74.99, 0), # Test out of stock
        ("978-0132350884", "Clean Code", "Robert C. Martin", 45.00, 7),
        ("978-1492056301", "Designing Data-Intensive Applications", "Martin Kleppmann", 65.50, 3)
    ],
    "carts": [
        ("john99", "978-0132350884", 1)
    ]
}

def wipe_and_seed_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            hash TEXT NOT NULL,
            role TEXT NOT NULL
        )''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            isbn TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            username TEXT,
            isbn TEXT,
            quantity INTEGER,
            PRIMARY KEY (username, isbn)
        )''')

    cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", fake_data["users"])
    cursor.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?)", fake_data["books"])
    cursor.executemany("INSERT INTO carts VALUES (?, ?, ?)", fake_data["carts"])

    conn.commit()
    conn.close()

if __name__ == '__main__':
    wipe_and_seed_db()