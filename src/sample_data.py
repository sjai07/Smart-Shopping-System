from database import Database

def populate_sample_data():
    db = Database()
    
    # Add sample customers
    db.cursor.execute('''
    INSERT INTO customers (name, age, gender, location, registration_date)
    VALUES 
    ('John Doe', 30, 'M', 'New York', '2024-01-01'),
    ('Jane Smith', 25, 'F', 'Los Angeles', '2024-01-02')
    ''')

    # Add sample products
    db.cursor.execute('''
    INSERT INTO products (name, category, price, description)
    VALUES 
    ('Laptop', 'Electronics', 999.99, 'High-performance laptop'),
    ('Smartphone', 'Electronics', 699.99, 'Latest smartphone'),
    ('T-shirt', 'Clothing', 29.99, 'Cotton T-shirt'),
    ('Jeans', 'Clothing', 59.99, 'Blue jeans')
    ''')

    # Add sample purchase history
    db.cursor.execute('''
    INSERT INTO purchases (customer_id, product_id, purchase_date, price)
    VALUES 
    (1, 1, '2024-01-10', 999.99),
    (1, 2, '2024-01-15', 699.99),
    (2, 3, '2024-01-12', 29.99)
    ''')

    db.conn.commit()

if __name__ == "__main__":
    populate_sample_data()