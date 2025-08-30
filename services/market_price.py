import requests
from fastapi import HTTPException
from bs4 import BeautifulSoup

# Mock market price data (capitalized keys to match dataset)
market_prices = {
    "Rice": 60,
    "Maize": 45,
    "Chickpea": 70,
    "Kidneybeans": 80,
    "Pigeonpeas": 75,
    "Mothbeans": 65,
    "Mungbean": 70,
    "Blackgram": 75,
    "Lentil": 80,
    "Pomegranate": 90,
    "Banana": 50,
    "Mango": 100,
    "Grapes": 120,
    "Watermelon": 40,
    "Muskmelon": 45,
    "Apple": 150,
    "Orange": 130,
    "Papaya": 60,
    "Coconut": 80,
    "Cotton": 70,
    "Jute": 65,
    "Coffee": 110
}

def fetch_market_price(crop: str):
    try:
        # Mock response for testing
        price = market_prices.get(crop, 50.0)  # Default to 50 if crop not found
        return {"crop": crop, "market_price": round(float(price), 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market price error: {str(e)}")