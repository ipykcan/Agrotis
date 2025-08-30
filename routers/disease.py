from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from services.disease_detection import predict_disease
from services.cache import save_to_cache, get_from_cache
import hashlib

router = APIRouter(prefix="/disease", tags=["disease"])

class DiseaseResponse(BaseModel):
    disease: str
    confidence: float
    recommendation: str

@router.post("/", response_model=DiseaseResponse)
async def detect_disease(file: UploadFile = File(...)):
    # Hash image content for cache key
    image_data = await file.read()
    request_hash = hashlib.md5(image_data).hexdigest()
    request = {"image_hash": request_hash}
    # Check cache
    cached = get_from_cache("disease", request)
    if cached:
        return cached
    # Reset file pointer
    file.file.seek(0)
    # Compute and cache
    result = await predict_disease(file)
    save_to_cache("disease", request, result)
    return result