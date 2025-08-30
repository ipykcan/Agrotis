from fastapi import APIRouter
from pydantic import BaseModel
from services.satellite_data import fetch_soil_data
from services.cache import save_to_cache, get_from_cache

router = APIRouter(prefix="/satellite", tags=["satellite"])

class SatelliteRequest(BaseModel):
    coordinates: dict
    date_range: dict

class SatelliteResponse(BaseModel):
    ndvi: float
    health_status: str
    soil_ph: float
    soil_nitrogen: float
    soil_org_carbon: float
    soil_water_content: float
    recommendation: str

@router.post("/", response_model=SatelliteResponse)
def get_satellite_data(req: SatelliteRequest):
    cached = get_from_cache("satellite", req.dict())
    if cached:
        return cached
    result = fetch_soil_data(req.coordinates, req.date_range)
    save_to_cache("satellite", req.dict(), result)
    return result