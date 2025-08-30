from fastapi import APIRouter
from pydantic import BaseModel
from services.market_price import fetch_market_price
from services.cache import save_to_cache, get_from_cache

router = APIRouter(prefix="/market", tags=["market"])

class MarketRequest(BaseModel):
    crop: str

class MarketResponse(BaseModel):
    crop: str
    market_price: float

@router.post("/", response_model=MarketResponse)
def get_market_price(req: MarketRequest):
    # Check cache
    cached = get_from_cache("market", req.dict())
    if cached:
        return cached
    # Compute and cache
    result = fetch_market_price(req.crop)
    save_to_cache("market", req.dict(), result)
    return result