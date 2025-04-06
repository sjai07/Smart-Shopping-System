# Package initialization for data integrations
import os
import sys

# Add the parent directory to sys.path when running as script
if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))    
    from src.integrations.base_integration import BaseIntegration
    from src.integrations.amazon_integration import AmazonIntegration
else:
    from .base_integration import BaseIntegration
    from .amazon_integration import AmazonIntegration

__all__ = ['BaseIntegration', 'AmazonIntegration']