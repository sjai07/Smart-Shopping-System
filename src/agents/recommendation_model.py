import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationModel:
    def __init__(self):
        self.data = None
        self.item_similarity_matrix = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def load_data(self, data_path):
        """Load and preprocess the product recommendation data."""
        self.data = pd.read_csv(data_path)
        
    def preprocess_data(self):
        """Preprocess the data for training the recommendation model."""
        # Encode categorical variables
        categorical_cols = ['Category', 'Subcategory', 'Brand', 'Season', 'Geographical_Location']
        for col in categorical_cols:
            self.label_encoders[col] = LabelEncoder()
            self.data[f'{col}_encoded'] = self.label_encoders[col].fit_transform(self.data[col])
        
        # Convert boolean columns to numeric
        self.data['Holiday'] = self.data['Holiday'].map({'Yes': 1, 'No': 0})
        
        # Scale numerical features
        numerical_cols = ['Price', 'Average_Rating_of_Similar_Products', 'Product_Rating', 
                         'Customer_Review_Sentiment_Score']
        self.data[numerical_cols] = self.scaler.fit_transform(self.data[numerical_cols])
        
    def build_item_similarity_matrix(self):
        """Build item similarity matrix using product features."""
        feature_cols = [
            'Category_encoded', 'Subcategory_encoded', 'Price',
            'Brand_encoded', 'Average_Rating_of_Similar_Products',
            'Product_Rating', 'Customer_Review_Sentiment_Score',
            'Holiday', 'Season_encoded', 'Geographical_Location_encoded'
        ]
        
        # Calculate cosine similarity between items
        item_features = self.data[feature_cols]
        self.item_similarity_matrix = cosine_similarity(item_features)
        
    def get_similar_products(self, product_id, n_recommendations=5):
        """Get similar products based on item similarity."""
        if product_id not in self.data['Product_ID'].values:
            return []
            
        # Get the index of the product
        idx = self.data[self.data['Product_ID'] == product_id].index[0]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.item_similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar products (excluding itself)
        sim_scores = sim_scores[1:n_recommendations+1]
        product_indices = [i[0] for i in sim_scores]
        
        return self.data.iloc[product_indices][['Product_ID', 'Category', 'Subcategory', 'Brand', 'Price']]
    
    def get_seasonal_recommendations(self, season, category=None, n_recommendations=5):
        """Get recommendations based on season and optionally category."""
        season_data = self.data[self.data['Season'] == season]
        
        if category:
            season_data = season_data[season_data['Category'] == category]
        
        # Sort by product rating and sentiment score
        season_data['score'] = season_data['Product_Rating'] * 0.7 + \
                              season_data['Customer_Review_Sentiment_Score'] * 0.3
        
        return season_data.nlargest(n_recommendations, 'score')[['Product_ID', 'Category', 'Subcategory', 'Brand', 'Price']]
    
    def get_personalized_recommendations(self, user_preferences, n_recommendations=5):
        """Get personalized recommendations based on user preferences."""
        # Filter based on user preferences
        filtered_data = self.data.copy()
        
        if 'preferred_categories' in user_preferences:
            filtered_data = filtered_data[filtered_data['Category'].isin(user_preferences['preferred_categories'])]
            
        if 'price_range' in user_preferences:
            min_price, max_price = user_preferences['price_range']
            filtered_data = filtered_data[
                (filtered_data['Price'] >= min_price) & 
                (filtered_data['Price'] <= max_price)
            ]
            
        if 'preferred_brands' in user_preferences:
            filtered_data = filtered_data[filtered_data['Brand'].isin(user_preferences['preferred_brands'])]
        
        # Sort by relevance score
        filtered_data['relevance_score'] = \
            filtered_data['Product_Rating'] * 0.4 + \
            filtered_data['Customer_Review_Sentiment_Score'] * 0.3 + \
            filtered_data['Average_Rating_of_Similar_Products'] * 0.3
            
        return filtered_data.nlargest(n_recommendations, 'relevance_score')[['Product_ID', 'Category', 'Subcategory', 'Brand', 'Price']]