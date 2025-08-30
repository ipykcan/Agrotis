import joblib
import pandas as pd
from models.schemas import CropRequest
from services.satellite_data import fetch_soil_data  # Correct import
from services.market_price import fetch_market_price

# Load the pre-trained RandomForest model
model = joblib.load("ml/crop_model.pkl")

# Crop-specific yield and sustainability data (capitalized keys to match dataset)
crop_data = {
    "Rice": {"base_yield": 1500, "sustainability_factor": 0.7, "cost_per_kg": 25},
    "Maize": {"base_yield": 1000, "sustainability_factor": 0.85, "cost_per_kg": 15},
    "Chickpea": {"base_yield": 800, "sustainability_factor": 0.9, "cost_per_kg": 30},
    "Kidneybeans": {"base_yield": 700, "sustainability_factor": 0.88, "cost_per_kg": 35},
    "Pigeonpeas": {"base_yield": 750, "sustainability_factor": 0.87, "cost_per_kg": 32},
    "Mothbeans": {"base_yield": 600, "sustainability_factor": 0.86, "cost_per_kg": 28},
    "Mungbean": {"base_yield": 650, "sustainability_factor": 0.89, "cost_per_kg": 30},
    "Blackgram": {"base_yield": 700, "sustainability_factor": 0.88, "cost_per_kg": 33},
    "Lentil": {"base_yield": 600, "sustainability_factor": 0.9, "cost_per_kg": 34},
    "Pomegranate": {"base_yield": 900, "sustainability_factor": 0.85, "cost_per_kg": 40},
    "Banana": {"base_yield": 1200, "sustainability_factor": 0.75, "cost_per_kg": 20},
    "Mango": {"base_yield": 800, "sustainability_factor": 0.8, "cost_per_kg": 45},
    "Grapes": {"base_yield": 850, "sustainability_factor": 0.82, "cost_per_kg": 50},
    "Watermelon": {"base_yield": 1100, "sustainability_factor": 0.78, "cost_per_kg": 18},
    "Muskmelon": {"base_yield": 1000, "sustainability_factor": 0.79, "cost_per_kg": 20},
    "Apple": {"base_yield": 900, "sustainability_factor": 0.83, "cost_per_kg": 60},
    "Orange": {"base_yield": 950, "sustainability_factor": 0.84, "cost_per_kg": 55},
    "Papaya": {"base_yield": 1100, "sustainability_factor": 0.76, "cost_per_kg": 25},
    "Coconut": {"base_yield": 500, "sustainability_factor": 0.9, "cost_per_kg": 35},
    "Cotton": {"base_yield": 700, "sustainability_factor": 0.7, "cost_per_kg": 30},
    "Jute": {"base_yield": 800, "sustainability_factor": 0.72, "cost_per_kg": 28},
    "Coffee": {"base_yield": 600, "sustainability_factor": 0.85, "cost_per_kg": 50}
}

def predict_crop(input_data: dict, use_satellite: bool = False, coordinates: dict = None, date_range: dict = None):
    # Use satellite data if requested
    if use_satellite and coordinates and date_range:
        satellite_data = fetch_soil_data(coordinates, date_range)  # Fixed function name
        input_data = {
            'pH_Value': satellite_data['soil_ph'],
            'Nitrogen': satellite_data['soil_nitrogen'],
            'Phosphorus': input_data.get('p', 40),
            'Potassium': input_data.get('k', 200),
            'Rainfall': input_data.get('rainfall', 900),
            'Temperature': input_data.get('temperature', 25),
            'Humidity': input_data.get('humidity', 70),
            'market_price': input_data.get('market_price', 50)
        }
    else:
        # Rename input keys to match training feature names
        input_data = {
            'pH_Value': input_data['ph'],
            'Nitrogen': input_data['n'],
            'Phosphorus': input_data['p'],
            'Potassium': input_data['k'],
            'Rainfall': input_data['rainfall'],
            'Temperature': input_data['temperature'],
            'Humidity': input_data.get('humidity', 70),
            'market_price': input_data['market_price']
        }
    
    # Create DataFrame for prediction (exclude market_price)
    model_input = {
        'Nitrogen': input_data['Nitrogen'],
        'Phosphorus': input_data['Phosphorus'],
        'Potassium': input_data['Potassium'],
        'Temperature': input_data['Temperature'],
        'Humidity': input_data['Humidity'],
        'pH_Value': input_data['pH_Value'],
        'Rainfall': input_data['Rainfall']
    }
    input_df = pd.DataFrame([model_input])
    
    # Predict the best crop
    prediction = model.predict(input_df)[0]
    
    # Fetch market price for the predicted crop
    market_price_data = fetch_market_price(prediction)
    market_price = market_price_data["market_price"]
    
    # Calculate yield, profit, and sustainability
    base_yield = crop_data[prediction]["base_yield"]
    yield_modifier = (input_data['pH_Value'] / 7.0) * (input_data['Rainfall'] / 900) * (input_data['Temperature'] / 25)
    expected_yield = base_yield * min(max(yield_modifier, 0.5), 1.5)
    revenue = expected_yield * market_price
    cost = expected_yield * crop_data[prediction]["cost_per_kg"]
    profit = revenue - cost
    sustainability_score = crop_data[prediction]["sustainability_factor"] * (input_data['Nitrogen'] / 100) * (input_data['Phosphorus'] / 40)
    sustainability_score = min(max(sustainability_score, 0.0), 1.0)
    
    # Explainable AI: Generate reasons for recommendation
    explanation = []
    if input_data['pH_Value'] >= 6.0 and input_data['pH_Value'] <= 7.5:
        explanation.append(f"The soil pH ({input_data['pH_Value']:.1f}) is ideal for {prediction} growth.")
    else:
        explanation.append(f"The soil pH ({input_data['pH_Value']:.1f}) is slightly off for {prediction}, consider soil amendments.")
    if input_data['Rainfall'] >= 700 and input_data['Rainfall'] <= 1000:
        explanation.append(f"Rainfall ({input_data['Rainfall']:.0f} mm) is suitable for {prediction}.")
    if input_data['Temperature'] >= 20 and input_data['Temperature'] <= 30:
        explanation.append(f"Temperature ({input_data['Temperature']:.0f}°C) is optimal for {prediction}.")
    if input_data['Humidity'] >= 60 and input_data['Humidity'] <= 80:
        explanation.append(f"Humidity ({input_data['Humidity']:.0f}%) is suitable for {prediction}.")
    explanation.append(f"Market price (₹{market_price:.0f}) makes {prediction} profitable with estimated profit of ₹{profit:.0f}.")
    if use_satellite:
        explanation.append(f"Recommendation based on satellite soil data for coordinates ({coordinates['lat']}, {coordinates['lon']}).")
    
    return {
        "crop": prediction,
        "expected_yield": round(expected_yield, 2),
        "profit": round(profit, 2),
        "sustainability_score": round(sustainability_score, 2),
        "explanation": explanation
    }