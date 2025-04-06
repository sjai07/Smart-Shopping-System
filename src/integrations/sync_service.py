from typing import Dict, List, Any
from datetime import datetime, timedelta
import threading
import time

import os
import sys

# Add the project root directory to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from src.integrations.base_integration import BaseIntegration
    from src.database import Database
except ImportError:
    # For direct file execution
    from base_integration import BaseIntegration
    from database import Database

class SyncService:
    def __init__(self, db: Database, integration: BaseIntegration, sync_interval: int = 3600):
        self.db = db
        self.integration = integration
        self.sync_interval = sync_interval  # in seconds
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_sync = {}
        self._sync_thread = None
        self._stop_event = threading.Event()
    
    def start(self):
        """Start the synchronization service"""
        if self._sync_thread is None:
            self._stop_event.clear()
            self._sync_thread = threading.Thread(target=self._sync_loop)
            self._sync_thread.daemon = True
            self._sync_thread.start()
    
    def stop(self):
        """Stop the synchronization service"""
        if self._sync_thread is not None:
            self._stop_event.set()
            self._sync_thread.join()
            self._sync_thread = None
    
    def _sync_loop(self):
        """Main synchronization loop"""
        while not self._stop_event.is_set():
            self.sync_all()
            time.sleep(self.sync_interval)
    
    def sync_all(self):
        """Synchronize all data from integration source"""
        try:
            # Sync products by category
            categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
            for category in categories:
                if self._should_sync('products', category):
                    products = self.integration.fetch_products(category=category)
                    self._update_products(products)
                    self.last_sync[f'products_{category}'] = datetime.now()
            
            # Sync prices and inventory for existing products
            product_ids = self._get_product_ids()
            if product_ids and self._should_sync('prices'):
                prices = self.integration.fetch_prices(product_ids)
                self._update_prices(prices)
                self.last_sync['prices'] = datetime.now()
            
            if product_ids and self._should_sync('inventory'):
                inventory = self.integration.fetch_inventory(product_ids)
                self._update_inventory(inventory)
                self.last_sync['inventory'] = datetime.now()
                
        except Exception as e:
            print(f'Sync failed: {str(e)}')
    
    def _should_sync(self, data_type: str, category: str = None) -> bool:
        """Check if data type needs synchronization"""
        key = f'{data_type}_{category}' if category else data_type
        last_sync_time = self.last_sync.get(key)
        if not last_sync_time:
            return True
        return (datetime.now() - last_sync_time).total_seconds() >= self.sync_interval
    
    def _update_products(self, products: List[Dict[str, Any]]):
        """Update products in database"""
        for product in products:
            query = """
            INSERT OR REPLACE INTO products 
            (product_id, name, category, price, description)
            VALUES (?, ?, ?, ?, ?)
            """
            self.db.cursor.execute(query, (
                product['product_id'],
                product['name'],
                product['category'],
                product['price'],
                product['description']
            ))
        self.db.conn.commit()
    
    def _update_prices(self, prices: Dict[str, float]):
        """Update product prices in database"""
        for product_id, price in prices.items():
            query = "UPDATE products SET price = ? WHERE product_id = ?"
            self.db.cursor.execute(query, (price, product_id))
        self.db.conn.commit()
    
    def _update_inventory(self, inventory: Dict[str, int]):
        """Update inventory levels in cache"""
        self.cache['inventory'] = {
            'data': inventory,
            'timestamp': datetime.now()
        }
    
    def _get_product_ids(self) -> List[str]:
        """Get all product IDs from database"""
        query = "SELECT product_id FROM products"
        self.db.cursor.execute(query)
        return [row[0] for row in self.db.cursor.fetchall()]
    
    def get_product_data(self, product_id: str) -> Dict[str, Any]:
        """Get product data with real-time price and inventory"""
        query = "SELECT * FROM products WHERE product_id = ?"
        self.db.cursor.execute(query, (product_id,))
        product = self.db.cursor.fetchone()
        
        if not product:
            return None
        
        # Check cache for inventory
        inventory_cache = self.cache.get('inventory', {})
        if inventory_cache and (datetime.now() - inventory_cache['timestamp']).total_seconds() < self.cache_timeout:
            inventory = inventory_cache['data'].get(product_id, 0)
        else:
            inventory = self.integration.fetch_inventory([product_id]).get(product_id, 0)
        
        return {
            'product_id': product[0],
            'name': product[1],
            'category': product[2],
            'price': product[3],
            'description': product[4],
            'inventory': inventory
        }