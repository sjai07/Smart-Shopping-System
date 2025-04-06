import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Tuple
from src.orchestrator import SmartShoppingSystem
from prometheus_client import make_asgi_app, Counter, Histogram, CollectorRegistry
from pythonjsonlogger import jsonlogger
import sys

# Configure JSON logging
logger = logging.getLogger()
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setFormatter(jsonlogger.JsonFormatter())
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Create a custom registry for our metrics
CUSTOM_REGISTRY = CollectorRegistry()

# Initialize metrics with custom registry
REQUEST_COUNT = Counter('shopping_recommendation_request_count', 'Count of shopping recommendation requests', registry=CUSTOM_REGISTRY)
RECOMMENDATION_LATENCY = Histogram('shopping_recommendation_duration_seconds', 'Duration of shopping recommendation generation', registry=CUSTOM_REGISTRY)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Shopping Recommendation System",
    description="API for generating personalized shopping recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics endpoint with custom registry
metrics_app = make_asgi_app(registry=CUSTOM_REGISTRY)
app.mount("/metrics", metrics_app)

# Initialize shopping system
shopping_system = SmartShoppingSystem()

class UserPreferences(BaseModel):
    preferred_categories: Optional[List[str]] = None
    price_range: Optional[Tuple[float, float]] = None
    preferred_brands: Optional[List[str]] = None

class RecommendationResponse(BaseModel):
    product_id: str
    name: str
    category: str
    price: float

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/recommendations/{customer_id}", response_model=List[RecommendationResponse])
async def get_recommendations(customer_id: int):
    try:
        REQUEST_COUNT.inc()
        with RECOMMENDATION_LATENCY.time():
            recommendations = shopping_system.get_recommendations(customer_id)
            
        if not recommendations:
            logger.warning(f"No recommendations found for customer {customer_id}")
            return []
            
        return [
            RecommendationResponse(
                product_id=prod_id,
                name=name,
                category=category,
                price=price
            ) for prod_id, name, category, price in recommendations
        ]
    except Exception as e:
        logger.error(f"Error generating recommendations for customer {customer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating recommendations")

@app.post("/recommendations/personalized", response_model=List[RecommendationResponse])
async def get_personalized_recommendations(preferences: UserPreferences):
    try:
        REQUEST_COUNT.inc()
        with RECOMMENDATION_LATENCY.time():
            recommendations = shopping_system.get_personalized_recommendations(
                preferences.dict(exclude_unset=True)
            )
            
        if not recommendations:
            logger.warning("No recommendations found for given preferences")
            return []
            
        return [
            RecommendationResponse(
                product_id=prod_id,
                name=name,
                category=category,
                price=price
            ) for prod_id, name, category, price in recommendations
        ]
    except Exception as e:
        logger.error(f"Error generating personalized recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating recommendations")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)