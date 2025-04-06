import pandas as pd

# Read and clean customer data
df = pd.read_csv('data/customer_data_collection.csv')
print(f'Original records: {len(df)}')

# Remove duplicates keeping first occurrence
df = df.drop_duplicates(subset=['Customer_ID'])
print(f'Records after removing duplicates: {len(df)}')

# Keep only required columns
required_columns = ['Customer_ID', 'Age', 'Gender', 'Location']
df_cleaned = df[required_columns]

# Save cleaned data
df_cleaned.to_csv('data/cleaned_customer_data.csv', index=False)
print('Cleaned data saved to data/cleaned_customer_data.csv')