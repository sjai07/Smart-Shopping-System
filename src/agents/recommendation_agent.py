import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.base_agent import Agent
from agents.recommendation_model import RecommendationModel
import numpy as np
from datetime import datetime, timedelta

class RecommendationAgent(Agent):
    def __init__(self, name, database):
        super().__init__(name, database)
        self.recommendations = {}
        self.current_customer_id = None
        self.similarity_threshold = 0.3
        self.time_decay_factor = 0.8
        self.model = RecommendationModel()
        self.model.load_data('data/product_recommendation_data.csv')
        self.model.preprocess_data()
        self.model.build_item_similarity_matrix()
    
    def process(self, customer_data):
        if not isinstance(customer_data, dict):
            return False
        self.current_preferences = customer_data.get('preferences', {})
        self.current_customer_id = customer_data.get('customer_id')
        
        # Validate that we have the necessary data
        if not self.current_customer_id or not self.current_preferences:
            print(f"Debug: Invalid customer data - ID: {self.current_customer_id}, Preferences: {self.current_preferences}")
            return False
            
        # Get recommendations using the trained model
        user_preferences = {
            'preferred_categories': self.current_preferences.get('categories', []),
            'preferred_brands': self.current_preferences.get('brands', []),
            'price_range': self.current_preferences.get('price_range', [0, float('inf')])
        }
        
        # Get personalized recommendations
        self.recommendations['personalized'] = self.model.get_personalized_recommendations(
            user_preferences,
            n_recommendations=5
        )
        
        # Get seasonal recommendations
        current_season = self.get_current_season()
        self.recommendations['seasonal'] = self.model.get_seasonal_recommendations(
            season=current_season,
            n_recommendations=5
        )
        
        return True
    
    def get_current_season(self):
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Autumn'
            
    def get_similar_customers(self):
        if not self.current_customer_id:
            return []
        
        query = """
        WITH customer_categories AS (
            SELECT p.category, COUNT(*) as purchase_count
            FROM purchases pur
            JOIN products p ON pur.product_id = p.product_id
            WHERE pur.customer_id = ?
            GROUP BY p.category
        )
        SELECT DISTINCT c.customer_id
        FROM purchases pur2
        JOIN products p2 ON pur2.product_id = p2.product_id
        JOIN customers c ON pur2.customer_id = c.customer_id
        JOIN customer_categories cc ON p2.category = cc.category
        WHERE c.customer_id != ?
        GROUP BY c.customer_id
        HAVING COUNT(DISTINCT p2.category) >= (
            SELECT COUNT(*) FROM customer_categories
        ) * ?
        LIMIT 5
        """
        self.db.cursor.execute(query, (self.current_customer_id, self.current_customer_id, self.similarity_threshold))
        return [row[0] for row in self.db.cursor.fetchall()]
    
    def get_time_weighted_score(self, days_ago):
        return self.time_decay_factor ** (days_ago / 30)  # Decay based on months
    
    def get_collaborative_recommendations(self):
        similar_customers = self.get_similar_customers()
        if not similar_customers:
            return []
        
        current_date = datetime.now()
        query = """
        SELECT 
            p.product_id, 
            p.name, 
            p.price,
            pur.purchase_date,
            COUNT(*) as purchase_count,
            AVG(JULIANDAY(?) - JULIANDAY(pur.purchase_date)) as days_ago
        FROM purchases pur
        JOIN products p ON pur.product_id = p.product_id
        WHERE pur.customer_id IN ({}) AND
              p.product_id NOT IN (
                  SELECT product_id FROM purchases
                  WHERE customer_id = ?
              )
        GROUP BY p.product_id
        HAVING days_ago <= 180  -- Consider only last 6 months
        ORDER BY 
            purchase_count * POWER(?, days_ago/30) DESC  -- Apply time decay
        LIMIT 5
        """.format(','.join('?' * len(similar_customers)))
        
        self.db.cursor.execute(
            query, 
            (current_date.strftime('%Y-%m-%d'), 
             *similar_customers, 
             self.current_customer_id,
             self.time_decay_factor)
        )
        return self.db.cursor.fetchall()
    
    def get_category_recommendations(self):
        recommendations = []
        if not self.current_preferences:
            return recommendations
        
        top_categories = sorted(
            self.current_preferences.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for category, _ in top_categories:
            query = """
            SELECT p.product_id, p.name, p.price,
                   COUNT(*) as purchase_count
            FROM products p
            LEFT JOIN purchases pur ON p.product_id = pur.product_id
            WHERE p.category = ? AND
                  p.product_id NOT IN (
                      SELECT product_id FROM purchases
                      WHERE customer_id = ?
                  )
            GROUP BY p.product_id
            ORDER BY purchase_count DESC
            LIMIT 3
            """
            self.db.cursor.execute(query, (category, self.current_customer_id))
            recommendations.extend(self.db.cursor.fetchall())
        
        return recommendations
    
    def act(self):
        collaborative_recommendations = self.get_collaborative_recommendations()
        category_recommendations = self.get_category_recommendations()
        
        # Combine and deduplicate recommendations
        seen_products = set()
        final_recommendations = []
        
        # Weight between collaborative and category recommendations
        collab_weight = 0.7
        category_weight = 0.3
        
        # Score and combine recommendations
        scored_recommendations = {}
        
        # Score collaborative recommendations
        for rec in collaborative_recommendations:
            if rec[0] not in seen_products:
                product_id, name, price = rec[:3]
                purchase_count = rec[4]
                days_ago = rec[5]
                
                # Calculate time-weighted score
                time_score = self.get_time_weighted_score(days_ago)
                popularity_score = min(purchase_count / 10, 1)  # Normalize purchase count
                final_score = collab_weight * (0.7 * time_score + 0.3 * popularity_score)
                
                scored_recommendations[product_id] = {
                    'data': (product_id, name, price),
                    'score': final_score
                }
                seen_products.add(product_id)
        
        # Score category recommendations
        for rec in category_recommendations:
            product_id = rec[0]
            if product_id not in seen_products:
                purchase_count = rec[3]
                popularity_score = min(purchase_count / 10, 1)  # Normalize purchase count
                final_score = category_weight * popularity_score
                
                if product_id in scored_recommendations:
                    scored_recommendations[product_id]['score'] += final_score
                else:
                    scored_recommendations[product_id] = {
                        'data': rec[:3],
                        'score': final_score
                    }
        
        # Sort by final score and return top recommendations
        sorted_recommendations = sorted(
            scored_recommendations.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:10]
        
        return [item['data'] for item in sorted_recommendations]