from src.agents.customer_agent import CustomerAgent
from src.agents.recommendation_agent import RecommendationAgent
from src.database import Database

class SmartShoppingSystem:
    def __init__(self):
        self.db = Database()
        self.agents = {}
    
    def create_customer_agent(self, customer_id):
        agent_name = f"customer_agent_{customer_id}"
        self.agents[agent_name] = CustomerAgent(agent_name, self.db, customer_id)
        return agent_name
    
    def create_recommendation_agent(self):
        agent_name = "recommendation_agent"
        self.agents[agent_name] = RecommendationAgent(agent_name, self.db)
        return agent_name
    
    def get_recommendations(self, customer_id):
        # Create agents if they don't exist
        customer_agent_name = self.create_customer_agent(customer_id)
        rec_agent_name = self.create_recommendation_agent()
        
        # Get customer preferences
        customer_preferences = self.agents[customer_agent_name].act()
        
        # Ensure we have valid customer preferences
        if not customer_preferences or not isinstance(customer_preferences, dict):
            print(f"Debug: Invalid customer preferences format: {customer_preferences}")
            return []
        
        # Process preferences and get recommendations
        if not self.agents[rec_agent_name].process(customer_preferences):
            print("Debug: Failed to process customer preferences")
            return []
            
        recommendations = self.agents[rec_agent_name].act()
        
        # Ensure we have valid recommendations
        if not recommendations:
            print("Debug: No recommendations generated")
            return []
            
        # Update customer agent with recommendations
        self.agents[customer_agent_name].process(recommendations)
        
        return recommendations