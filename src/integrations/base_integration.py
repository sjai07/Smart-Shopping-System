from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime
import requests
import json

class BaseIntegration(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    @abstractmethod
    def fetch_products(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch products from the e-commerce platform"""
        pass
    
    @abstractmethod
    def fetch_prices(self, product_ids: List[str]) -> Dict[str, float]:
        """Fetch real-time prices for given products"""
        pass
    
    @abstractmethod
    def fetch_inventory(self, product_ids: List[str]) -> Dict[str, int]:
        """Fetch real-time inventory levels"""
        pass
    
    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None, data: Dict = None) -> Dict:
        """Make HTTP request to the API endpoint"""
        url = f'{self.base_url}/{endpoint}'
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'API request failed: {str(e)}')
            return {}
    
    def _handle_rate_limits(self, response: requests.Response) -> None:
        """Handle API rate limiting"""
        if 'X-RateLimit-Remaining' in response.headers:
            remaining = int(response.headers['X-RateLimit-Remaining'])
            if remaining < 10:
                print(f'Warning: Only {remaining} API calls remaining')
    
    def close(self) -> None:
        """Close the session"""
        self.session.close()