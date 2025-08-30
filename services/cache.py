import sqlite3
import json
from datetime import datetime, timedelta

def init_cache():
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            endpoint TEXT,
            request TEXT,
            response TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_cache(endpoint: str, request: dict, response: dict):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cache (endpoint, request, response, timestamp) VALUES (?, ?, ?, ?)",
        (endpoint, json.dumps(request), json.dumps(response), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_from_cache(endpoint: str, request: dict, max_age_hours: int = 24):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT response, timestamp FROM cache WHERE endpoint = ? AND request = ?",
        (endpoint, json.dumps(request))
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        response, timestamp = result
        cache_time = datetime.fromisoformat(timestamp)
        if datetime.now() - cache_time < timedelta(hours=max_age_hours):
            return json.loads(response)
    return None