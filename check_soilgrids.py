import requests

def check_soilgrids_response(lat, lon, buffer=0.5, coverage_id="awc_0-5cm_mean", property_name="awc"):
    url = f"https://maps.isric.org/mapserv?map=/map/{property_name}.map"
    params = {
        "SERVICE": "WCS",
        "VERSION": "2.0.1",
        "REQUEST": "GetCoverage",
        "COVERAGEID": coverage_id,
        "FORMAT": "GeoTIFF",
        "SUBSET": [
            f"long({lon - buffer},{lon + buffer})",
            f"lat({lat - buffer},{lat + buffer})"
        ]
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        print(f"Status Code: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        print(f"Content (first 200 chars): {r.content[:200]}")
        filename = f"soil_{property_name}_{lat}_{lon}.tif"
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"Saved file: {filename}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Test for Ranchi
check_soilgrids_response(lat=23.36, lon=85.33)