import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="data/smart_shopping.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # Customers table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            age INTEGER,
            gender TEXT,
            location TEXT,
            registration_date TEXT
        )''')

        # Products table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            description TEXT
        )''')

        # Browsing history table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS browsing_history (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            timestamp TEXT,
            action TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )''')

        # Purchase history table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            purchase_date TEXT,
            price REAL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )''')

        self.conn.commit()