from typing import Dict, List, Any
from base_integration import BaseIntegration
from datetime import datetime
from sp_api.api import Catalog
from sp_api.api import Products
from sp_api.api import Inventories
from sp_api.base import Marketplaces
from sp_api.base import SellingApiException

class AmazonIntegration(BaseIntegration):
    def __init__(self, api_key: str, secret_key: str, region: str = 'us-east-1'):
        super().__init__(api_key, 'https://sellingpartnerapi.amazon.com')
        self.secret_key = secret_key
        self.region = region
        self.marketplace_id = 'ATVPDKIKX0DER'  # US marketplace
        self.credentials = {
            'refresh_token': None,  # Will need to be set via OAuth flow
            'lwa_app_id': api_key,
            'lwa_client_secret': secret_key,
            'aws_access_key': api_key,
            'aws_secret_key': secret_key,
            'role_arn': None,  # Will need to be set based on SP API setup
        }
    
    def fetch_products(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch products from Amazon's catalog"""
        try:
            catalog_api = Catalog(credentials=self.credentials, marketplace=Marketplaces[self.region.upper()])
            params = {
                'MarketplaceId': self.marketplace_id,
                'MaxResultsPerPage': limit
            }
            if category:
                params['BrowseNodeId'] = self._get_browse_node_id(category)
            
            response = catalog_api.search_catalog_items(**params)
            products = []
            for item in response.payload.get('Items', []):
                product = {
                    'product_id': item.get('Identifiers', {}).get('MarketplaceASIN', {}).get('ASIN'),
                    'name': item.get('Summaries', [{}])[0].get('Title'),
                    'category': category or self._extract_category(item),
                    'price': self._extract_price(item),
                    'description': item.get('Summaries', [{}])[0].get('Description'),
                    'last_updated': datetime.now().isoformat()
                }
                if product['product_id']:
                    products.append(product)
            return products
        except SellingApiException as e:
            print(f'Failed to fetch Amazon products: {str(e)}')
            return []
    
    def fetch_prices(self, product_ids: List[str]) -> Dict[str, float]:
        """Fetch real-time prices for Amazon products"""
        prices = {}
        try:
            pricing_api = Pricing(credentials=self.credentials, marketplace=Marketplaces[self.region.upper()])
            for batch in self._batch_list(product_ids, 20):
                response = pricing_api.get_item_offers(asin=batch[0], ItemCondition='New')
                for item in response.payload.get('Summary', []):
                    price = item.get('LowestPrice', {}).get('Amount')
                    if price:
                        prices[batch[0]] = float(price)
            return prices
        except SellingApiException as e:
            print(f'Failed to fetch Amazon prices: {str(e)}')
            return prices
    
    def fetch_inventory(self, product_ids: List[str]) -> Dict[str, int]:
        """Fetch real-time inventory levels from Amazon"""
        inventory = {}
        try:
            inventory_api = Inventory(credentials=self.credentials, marketplace=Marketplaces[self.region.upper()])
            for batch in self._batch_list(product_ids, 20):
                response = inventory_api.get_inventory_summary_marketplace(asin=batch[0])
                for item in response.payload.get('inventorySummaries', []):
                    stock = item.get('totalQuantity', 0)
                    inventory[batch[0]] = stock
            return inventory
        except SellingApiException as e:
            print(f'Failed to fetch Amazon inventory: {str(e)}')
            return inventory
    
    def _get_browse_node_id(self, category: str) -> str:
        """Map category to Amazon browse node ID"""
        category_map = {
            'Electronics': '172282',
            'Clothing': '7141123011',
            'Books': '283155',
            'Home': '1055398',
            'Sports': '10971',
        }
        return category_map.get(category, '')
    
    def _extract_category(self, item: Dict) -> str:
        """Extract category from Amazon product data"""
        browse_nodes = item.get('BrowseNodes', [])
        if browse_nodes:
            return browse_nodes[0].get('Name', 'Unknown')
        return 'Unknown'
    
    def _extract_price(self, item: Dict) -> float:
        """Extract price from Amazon product data"""
        try:
            price_data = item.get('Price', {})
            return float(price_data.get('Amount', 0))
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def _batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
        """Split list into batches"""
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]