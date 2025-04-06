import sqlite3
import pandas as pd
from database import Database
from data_import import DataImporter

def main():
    # Clear existing data
    db = Database()
    db.cursor.execute('DELETE FROM customers')
    db.conn.commit()
    print('Cleared existing customer records')
    
    # Read and clean customer data
    df = pd.read_csv('data/customer_data_collection.csv')
    print(f'Original records: {len(df)}')
    
    # Keep only required columns
    required_columns = ['Customer_ID', 'Age', 'Gender', 'Location']
    df_cleaned = df[required_columns].drop_duplicates(subset=['Customer_ID'])
    print(f'Records after cleaning: {len(df_cleaned)}')
    
    # Save cleaned data
    cleaned_file = 'data/cleaned_customer_data.csv'
    df_cleaned.to_csv(cleaned_file, index=False)
    print(f'Cleaned data saved to {cleaned_file}')
    
    # Import cleaned data
    importer = DataImporter()
    importer.import_csv_data(cleaned_file, 'customers')

if __name__ == '__main__':
    main()