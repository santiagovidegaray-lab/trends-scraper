import time
from datetime import date
from supabase import create_client
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
SERPAPI_KEY = os.environ["SERPAPI_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

KEYWORDS = [
    'intermittent fasting',
    'creatine',
    'pilates',
    'ozempic',
    'gut health',
    'protein powder',
    'cold plunge',
    'cortisol'
]

def get_trend(keyword):
    params = {
        "engine": "google_trends",
        "q": keyword,
        "date": "today 3-m",
        "geo": "US",
        "cat": "45",
        "api_key": SERPAPI_KEY
    }
    response = requests.get("https://serpapi.com/search", params=params)
    return response.json()

def scrape_trends():
    today = date.today().isoformat()
    rows = []
    rising_rows = []

    for keyword in KEYWORDS:
        print(f"Procesando: {keyword}")
        try:
            data = get_trend(keyword)

            # interest over time
            timeline = data.get("interest_over_time", {}).get("timeline_data", [])
            if timeline:
                latest = timeline[-1]
                value = latest.get("values", [{}])[0].get("extracted_value", 0)
                rows.append({
                    "keyword": keyword,
                    "value": int(value),
                    "recorded_at": today,
                    "region": "US"
                })

            # rising queries
            rising = data.get("related_queries", {}).get("rising", [])
            for r in rising[:5]:
                rising_rows.append({
                    "parent_kw": keyword,
                    "query": r.get("query", ""),
                    "value": str(r.get("extracted_value", "Breakout")),
                    "recorded_at": today
                })

        except Exception as e:
            print(f"Error en {keyword}: {e}")

        time.sleep(2)

    if rows:
        supabase.table("trends").upsert(rows, on_conflict="keyword,recorded_at").execute()
        print(f"✓ {len(rows)} trends guardados")

    if rising_rows:
        supabase.table("rising_queries").insert(rising_rows).execute()
        print(f"✓ {len(rising_rows)} rising queries guardadas")

if __name__ == "__main__":
    scrape_trends()
