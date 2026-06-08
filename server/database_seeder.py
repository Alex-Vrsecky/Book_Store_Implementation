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
    # All Books in catalogue (customer view)
    "books": [
        ("978-0134092660", "Networking Essentials", "Cisco Press", 89.99, 12, True),
        ("978-1119642817", "CompTIA Security+ Study Guide", "Mike Chapple", 59.95, 25, True),
        ("978-0596009205", "Head First Design Patterns", "Eric Freeman", 74.99, 0, True), # Test out of stock
        ("978-0132350884", "Clean Code", "Robert C. Martin", 45.00, 7, True),
        ("978-1492056301", "Designing Data-Intensive Applications", "Martin Kleppmann", 65.50, 3, True),
    ],
    # All books in inventory (staff view)
    "inventory": [
        ("978-0134092660", "Networking Essentials", "Cisco Press", 89.99, 500, True),
        ("978-1119642817", "CompTIA Security+ Study Guide", "Mike Chapple", 59.95, 400, True),
        ("978-0596009205", "Head First Design Patterns", "Eric Freeman", 74.99, 320, True), # Test out of stock
        ("978-0132350884", "Clean Code", "Robert C. Martin", 45.00, 340, True),
        ("978-1492056301", "Designing Data-Intensive Applications", "Martin Kleppmann", 65.50, 340, True),
        ("978-1434209301", "Data Makes me Rage", "Homer Simpson", 105.50, 600, False),
        ("978-1412209451", "Data Structures Confuse Me", "Steve Irwin", 10.50, 400, False), # Test unpublished book
        ("978-1412454461", "Data Structures Anger Me", "Steve Irwin", 10.50, 400, False),
        ("978-1412388321", "Data Structures Are Fun", "Peninsula Ernst", 69.90, 500, False),
        ("978-1434409101", "Data Structures with Alex", "Alex Mon", 81.50, 500, False),
    ],
    # Carts for each user (only 1 at a time for each user)
    "carts": [
        ("john99", "978-0132350884", 1)
    ],

    # Orders placed by customers (staff view)
    "orders": [
        ("Order#9874", "john99", "5 Lonsdale Street", "2026-06-06", "FedEx", "Phillip Francis", "0493049609", "Processed")
    ],

    # Detailed description of specific orders (Customer View - Purchase History)
    "order_items": [
        ("Order#9874", "978-0134092660", "Networking Essentials", "Cisco Press", 2, 89.99)
    ],

    # Different delivery person for FedEx Courier Service
    "delivery_personnel": [
        ("POLER-MICHMA123", "Michelle Poller", "0432209390", "FedEx"),
        ("MANU-BOLA023", "Bolani Manula", "0433209233", "FedEx"),
        ("FRAN-PHIL394", "Phillip Francis", "0493049609", "FedEx"),
        ("DRIAM-ALEX353", "Alex Driamer", "0450331920", "FedEx"),
    ]
}

def wipe_and_seed_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()


    # CREATING user Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            hash TEXT NOT NULL,
            role TEXT NOT NULL
        )''')
    
    # CREATING Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            isbn TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            is_published BOOLEAN NOT NULL 
        )''')
    
    # CREATING Inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            isbn TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            is_published BOOLEAN NOT NULL
        )''')
    
    # CREATING Cart Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            username TEXT,
            isbn TEXT,
            quantity INTEGER,
            PRIMARY KEY (username, isbn)
        )''')
    
    # CREATING Order Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders(
            order_num TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            delivery_address TEXT NOT NULL,
            date_of_order_placed DATE NOT NULL,
            courier_name TEXT NOT NULL,
            delivery_person_name TEXT NOT NULL,
            delivery_person_phone TEXT NOT NULL,
            order_status TEXT NOT NULL                                
        )''')
        
    
# ORDER STATUS - Sequence > Processed, Shipped, In-transit, Delivered

    # CREATING Order_Item Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items(
            order_num TEXT,
            isbn TEXT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER,
            price REAL NOT NULL,
            FOREIGN KEY(order_num) REFERENCES orders(order_num)
        )''')
    
    # CREATING Delivery Person Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_personnel(
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            delivery_person_phone TEXT NOT NULL,
            courier_service_type TEXT NOT NULL
        )''')

    # INSERTS SET OF SEED DATA INTO MULTIPLE TABLES IN THE TFB.DB (FOR TESTING)
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", fake_data["users"])
    cursor.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?)", fake_data["books"])
    cursor.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)", fake_data["inventory"])
    cursor.executemany("INSERT INTO carts VALUES (?, ?, ?)", fake_data["carts"])
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)", fake_data["orders"])
    cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)", fake_data["order_items"])
    cursor.executemany("INSERT INTO delivery_personnel VALUES (?, ?, ?, ?)", fake_data["delivery_personnel"])



    conn.commit()
    conn.close()

if __name__ == '__main__':
    wipe_and_seed_db()