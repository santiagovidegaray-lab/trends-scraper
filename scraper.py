import time
from datetime import date
from pytrends.request import TrendReq
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

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

def scrape_trends():
    pytrends = TrendReq(hl='en-US', tz=360)
    today = date.today().isoformat()

    pytrends.build_payload(KEYWORDS, cat=45, timeframe='today 3-m', geo='US')
    time.sleep(5)
    df = pytrends.interest_over_time()

    rows = []
    for kw in KEYWORDS:
        if kw in df.columns:
            latest_value = int(df[kw].iloc[-1])
            rows.append({
                "keyword": kw,
                "value": latest_value,
                "recorded_at": today,
                "region": "US"
            })

    if rows:
        supabase.table("trends").upsert(rows, on_conflict="keyword,recorded_at").execute()
        print(f"✓ {len(rows)} trends guardados")

    time.sleep(5)

    related = pytrends.related_queries()
    rising_rows = []

    for kw in KEYWORDS:
        time.sleep(3)
        try:
            rising_df = related[kw]['rising']
            if rising_df is not None and not rising_df.empty:
                for _, row in rising_df.head(5).iterrows():
                    rising_rows.append({
                        "parent_kw": kw,
                        "query": row['query'],
                        "value": str(row['value']),
                        "recorded_at": today
                    })
        except Exception as e:
            print(f"Error en {kw}: {e}")

    if rising_rows:
        supabase.table("rising_queries").insert(rising_rows).execute()
        print(f"✓ {len(rising_rows)} rising queries guardadas")

if __name__ == "__main__":
    scrape_trends()
