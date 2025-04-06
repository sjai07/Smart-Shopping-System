import os
import sys

# Add the project root directory to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.agents.base_agent import Agent

class CustomerAgent(Agent):
    def __init__(self, name, database, customer_id):
        super().__init__(name, database)
        self.customer_id = customer_id
        self.preferences = {}
        self.category_weights = {}
        self.interaction_history = []
        self.load_customer_data()
    
    def load_customer_data(self):
        # Load customer data from database
        query = "SELECT * FROM customers WHERE customer_id = ?"
        self.db.cursor.execute(query, (self.customer_id,))
        self.customer_data = self.db.cursor.fetchone()
        
        if not self.customer_data:
            print(f"Debug: Customer {self.customer_id} not found in database")
            return
        
        # Load purchase history with time weighting
        query = """
        SELECT 
            p.category,
            COUNT(*) as purchase_count,
            MAX(JULIANDAY('now') - JULIANDAY(pur.purchase_date)) as days_since_last_purchase,
            AVG(p.price) as avg_price
        FROM purchases pur
        JOIN products p ON pur.product_id = p.product_id
        WHERE customer_id = ? AND
              pur.purchase_date >= date('now', '-1 year')
        GROUP BY p.category
        """
        self.db.cursor.execute(query, (self.customer_id,))
        
        purchase_data = self.db.cursor.fetchall()
        if not purchase_data:
            print(f"Debug: No purchase history found for customer {self.customer_id}")
            # Set default preferences for new customers
            self.preferences = {'Electronics': 0.5, 'Clothing': 0.5}
            return
            
        for category, count, days_ago, avg_price in purchase_data:
            # Calculate time-weighted preference
            time_weight = 1.0 / (1 + days_ago/365)  # Decay over a year
            price_weight = min(avg_price / 100, 1.0)  # Normalize price preference
            
            self.preferences[category] = count
            self.category_weights[category] = {
                'purchase_count': count,
                'time_weight': time_weight,
                'price_weight': price_weight,
                'total_weight': (0.5 * count/10 + 0.3 * time_weight + 0.2 * price_weight)
            }
            
        print(f"Debug: Loaded preferences for customer {self.customer_id}: {self.preferences}")
        print(f"Debug: Category weights: {self.category_weights}")
    
    def process(self, message):
        # Process incoming recommendations and update interaction history
        self.interaction_history.append({
            'recommendations': message,
            'timestamp': 'now'
        })
        return True
    
    def get_weighted_preferences(self):
        weighted_prefs = {}
        for category, weights in self.category_weights.items():
            weighted_prefs[category] = weights['total_weight']
        return weighted_prefs
    
    def act(self):
        # Return customer preferences and behavior data
        preferences = self.get_weighted_preferences()
        if not preferences and self.preferences:
            # Use direct preferences if weighted preferences are empty
            preferences = self.preferences
        
        return {
            'customer_id': self.customer_id,
            'preferences': preferences,
            'interaction_history': self.interaction_history[-5:] if self.interaction_history else []
        }