import requests
import rioxarray
from fastapi import HTTPException
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOILGRIDS_URL = "https://maps.isric.org/mapserv?map=/map/soilgrids.map"

VALID_PROPERTIES = {
    "ph": "phh2o_0-5cm_mean",
    "soc": "soc_0-5cm_mean",
    "sand": "sand_0-5cm_mean",
    "clay": "clay_0-5cm_mean",
    "silt": "silt_0-5cm_mean",
    "bdod": "bdod_0-5cm_mean"
}

def fetch_soil_property(lat, lon, buffer, coverage_id, property_name):
    params = {
        "SERVICE": "WCS",
        "VERSION": "2.0.1",
        "REQUEST": "GetCoverage",
        "COVERAGEID": coverage_id,
        "FORMAT": "image/tiff",
        "SUBSETTINGCRS": "http://www.opengis.net/def/crs/EPSG/0/4326",
        "SUBSET": f"Lat({lat - buffer},{lat + buffer}),Long({lon - buffer},{lon + buffer})"
    }
    try:
        full_url = requests.Request('GET', SOILGRIDS_URL, params=params).prepare().url
        logger.info(f"Sending request for {property_name}: {full_url}")
        r = requests.get(SOILGRIDS_URL, params=params, timeout=60)
        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "")
        if "image/tiff" not in content_type:
            logger.error(f"Invalid response for {property_name}: {r.text[:500]}")
            raise HTTPException(
                status_code=500,
                detail=f"Invalid response for {property_name}: {r.text[:200]}"
            )

        filename = Path(f"soil_{property_name}_{lat}_{lon}.tif")
        with open(filename, "wb") as f:
            f.write(r.content)

        data = rioxarray.open_rasterio(filename)
        mean_value = float(np.nanmean(data.values))
        logger.info(f"Fetched {property_name} for ({lat}, {lon}): {mean_value}")
        return mean_value
    except requests.HTTPError as e:
        logger.error(f"HTTP error for {property_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HTTP error fetching {property_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching {property_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching {property_name}: {str(e)}")

def estimate_awc(sand, clay, soc):
    organic_matter = soc / 10  # Convert SOC (g/kg) to %
    awc = 0.1 + 0.002 * clay + 0.001 * organic_matter - 0.0005 * sand
    return max(min(awc * 100, 30), 5)  # % range

def estimate_nitrogen(soc):
    return (soc / 12) * 1000  # mg/kg

def fetch_soil_data(coordinates: dict, date_range: dict):
    try:
        lat, lon = coordinates["lat"], coordinates["lon"]
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        buffer = 0.01

        ph_data = fetch_soil_property(lat, lon, buffer, VALID_PROPERTIES["ph"], "ph")
        soc_data = fetch_soil_property(lat, lon, buffer, VALID_PROPERTIES["soc"], "soc")
        sand_data = fetch_soil_property(lat, lon, buffer, VALID_PROPERTIES["sand"], "sand")
        clay_data = fetch_soil_property(lat, lon, buffer, VALID_PROPERTIES["clay"], "clay")

        awc_data = estimate_awc(sand_data, clay_data, soc_data)
        nitrogen_data = estimate_nitrogen(soc_data)

        ndvi = 0.51
        org_carbon = soc_data / 10
        health_status = "Healthy" if ndvi > 0.6 else "Stressed"

        return {
            "ndvi": ndvi,
            "health_status": health_status,
            "soil_ph": float(ph_data / 10),  # SoilGrids pH is in pH*10 units
            "soil_nitrogen": float(nitrogen_data),
            "soil_org_carbon": float(org_carbon),
            "soil_water_content": float(awc_data),
            "recommendation": (
                f"Crop health: {health_status}. Monitor irrigation (AWC: {awc_data:.2f}%). "
                f"Adjust pH ({ph_data/10:.2f}) and nitrogen ({nitrogen_data:.2f} mg/kg) if needed."
            )
        }
    except Exception as e:
        logger.error(f"Failed to fetch soil data: {str(e)}")
        return {
            "ndvi": 0.51,
            "health_status": "Stressed",
            "soil_ph": 6.5,
            "soil_nitrogen": 100.0,
            "soil_org_carbon": 1.65,
            "soil_water_content": 20.0,
            "recommendation": "Using mock soil data due to API error."
        }