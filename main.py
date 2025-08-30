from fastapi import FastAPI
from routers import recommendations, disease, chat, satellite, market
from services.cache import init_cache

app = FastAPI(title="AI Crop Recommendation Backend")

# Initialize cache
init_cache()

app.include_router(recommendations.router)
app.include_router(disease.router)
app.include_router(chat.router)
app.include_router(satellite.router)
app.include_router(market.router)

@app.get("/")
def read_root():
    return {"message": "AI Crop Recommendation Backend is running"}