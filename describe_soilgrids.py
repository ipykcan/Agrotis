import requests

def describe_coverage(coverage_id="awc_0-5cm_mean"):
    url = "https://maps.isric.org/mapserv?map=/map/awc.map"
    params = {
        "SERVICE": "WCS",
        "VERSION": "2.0.1",
        "REQUEST": "DescribeCoverage",
        "COVERAGEID": coverage_id
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        print(f"Status Code: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        print(f"Response: {r.content.decode()[:500]}")
    except Exception as e:
        print(f"Error: {str(e)}")

describe_coverage()