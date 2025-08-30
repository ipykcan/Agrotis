from fastapi import APIRouter
from pydantic import BaseModel
from services.crop_recommendation import predict_crop
from services.cache import save_to_cache, get_from_cache

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

class CropRequest(BaseModel):
    ph: float
    n: float
    p: float
    k: float
    rainfall: float
    temperature: float
    humidity: float
    market_price: float
    use_satellite: bool = False
    coordinates: dict | None = None
    date_range: dict | None = None

class CropResponse(BaseModel):
    crop: str
    expected_yield: float
    profit: float
    sustainability_score: float
    explanation: list[str]

@router.post("/", response_model=CropResponse)
def get_recommendation(req: CropRequest):
    # Check cache
    cached = get_from_cache("recommendations", req.dict())
    if cached:
        return cached
    # Compute and cache
    result = predict_crop(req.dict(), req.use_satellite, req.coordinates, req.date_range)
    save_to_cache("recommendations", req.dict(), result)
    return result