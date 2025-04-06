import pandas as pd
import sqlite3
from database import Database
from datetime import datetime

class DataImporter:
    def __init__(self, db_path="data/smart_shopping.db"):
        self.db = Database(db_path)
    
    def validate_customer_data(self, df):
        required_columns = ['Customer_ID', 'Age', 'Gender', 'Location']
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"Missing required columns: {missing}")
        
        # Validate data types
        if not df['Age'].dtype.kind in 'iu':  # Check if age is integer
            raise ValueError("Age must be an integer")
        if not df['Gender'].isin(['Male', 'Female', 'Other']).all():
            raise ValueError("Gender must be 'Male', 'Female', or 'Other'")
    
    def validate_product_data(self, df):
        required_columns = ['Product_ID', 'Category', 'Price', 'Brand']
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"Missing required columns: {missing}")
        
        # Validate data types
        if not pd.to_numeric(df['Price'], errors='coerce').notna().all():
            raise ValueError("Price must be numeric")
    
    def validate_purchase_data(self, df):
        required_columns = ['customer_id', 'product_id', 'purchase_date', 'price']
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"Missing required columns: {missing}")
        
        # Validate data types and references
        if not pd.to_numeric(df['price'], errors='coerce').notna().all():
            raise ValueError("Price must be numeric")
        
        # Validate dates
        try:
            pd.to_datetime(df['purchase_date'])
        except:
            raise ValueError("Invalid purchase_date format")
    
    def import_csv_data(self, file_path, table_type):
        """Import data from CSV file
        
        Args:
            file_path (str): Path to the CSV file
            table_type (str): Type of data ('customers', 'products', or 'purchases')
        """
        try:
            df = pd.read_csv(file_path)
            
            # Validate data based on type
            if table_type == 'customers':
                self.validate_customer_data(df)
                for _, row in df.iterrows():
                    self.db.cursor.execute(
                        'INSERT INTO customers (customer_id, age, gender, location, registration_date) VALUES (?, ?, ?, ?, ?)',
                        (row['Customer_ID'], row['Age'], row['Gender'], row['Location'], datetime.now().strftime('%Y-%m-%d'))
                    )
            
            elif table_type == 'products':
                self.validate_product_data(df)
                for _, row in df.iterrows():
                    self.db.cursor.execute(
                        'INSERT INTO products (product_id, name, category, price, description) VALUES (?, ?, ?, ?, ?)',
                        (row['Product_ID'], row['Brand'], row['Category'], row['Price'], row['Subcategory'])
                    )
            
            elif table_type == 'purchases':
                self.validate_purchase_data(df)
                for _, row in df.iterrows():
                    self.db.cursor.execute(
                        'INSERT INTO purchases (customer_id, product_id, purchase_date, price) VALUES (?, ?, ?, ?)',
                        (row['customer_id'], row['product_id'], row['purchase_date'], row['price'])
                    )
            
            self.db.conn.commit()
            print(f"Successfully imported {len(df)} records into {table_type}")
            
        except Exception as e:
            self.db.conn.rollback()
            raise Exception(f"Error importing data: {str(e)}")
    
    def import_json_data(self, file_path, table_type):
        """Import data from JSON file
        
        Args:
            file_path (str): Path to the JSON file
            table_type (str): Type of data ('customers', 'products', or 'purchases')
        """
        try:
            df = pd.read_json(file_path)
            self.import_csv_data(df, table_type)  # Reuse CSV import logic
        except Exception as e:
            raise Exception(f"Error importing JSON data: {str(e)}")

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(
        description='Import data into the smart shopping database',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument('file_path', 
                        help='Path to the data file (must be .csv or .json)')
    parser.add_argument('table_type', 
                        choices=['customers', 'products', 'purchases'],
                        help='Type of data to import (customers/products/purchases)')
    
    parser.add_argument('--db-path',
                        default='data/smart_shopping.db',
                        help='Path to the database file (default: data/smart_shopping.db)')
    
    # Add usage examples
    parser.usage = f"{parser.format_usage().rstrip()}\n\nExamples:\n"
    parser.usage += "  # Import customer data from CSV:\n"
    parser.usage += "  python src/data_import.py data/customers.csv customers\n\n"
    parser.usage += "  # Import product data from JSON:\n"
    parser.usage += "  python src/data_import.py data/products.json products\n\n"
    parser.usage += "  # Import purchase history with custom database path:\n"
    parser.usage += "  python src/data_import.py data/purchases.csv purchases --db-path custom.db"
    
    args = parser.parse_args()
    
    try:
        # Validate file path
        if not os.path.exists(args.file_path):
            raise FileNotFoundError(f"Error: File not found - {args.file_path}")
            
        # Determine file type and import accordingly
        file_ext = os.path.splitext(args.file_path)[1].lower()
        if file_ext not in ['.csv', '.json']:
            raise ValueError(f"Error: Unsupported file type '{file_ext}'. Please use .csv or .json files")
        
        # Initialize importer with custom database path
        importer = DataImporter(db_path=args.db_path)
        
        # Import data based on file type
        if file_ext == '.csv':
            importer.import_csv_data(args.file_path, args.table_type)
        else:  # .json
            importer.import_json_data(args.file_path, args.table_type)
            
        print(f"Success: Imported data from '{args.file_path}' into {args.table_type} table")
        
    except Exception as e:
        print(str(e))
        parser.print_help()
        exit(1)