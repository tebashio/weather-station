import requests
import json
import time
import sys

def fetch_weather():
    print("--- Data Synchronization Engine Starting ---")
    
    # 1. 観測地点リストの読み込み
    try:
        with open('locations.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load locations.json: {e}")
        sys.exit(1)

    # 2. Open-Meteo API 一括リクエスト
    # 日本全土142地点を一気に取得するための準備
    lats = ",".join([str(l['lat']) for l in locations])
    lons = ",".join([str(l['lon']) for l in locations])
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=surface_pressure&past_days=3&forecast_days=11&timezone=Asia%2FTokyo"
    
    try:
        print(f"Requesting data for {len(locations)} locations...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # Open-Meteo APIは複数地点リクエスト時にリストを返す
        responses = data if isinstance(data, list) else [data]
        
        results = {}
        for i, loc in enumerate(locations):
            # 取得したデータをID（loc_XXX）をキーにして格納
            point_data = responses[i]
            hourly = point_data.get('hourly', {})
            times = hourly.get('time', [])
            pressures = hourly.get('surface_pressure', [])
            
            # 1地点の全履歴
            results[loc['id']] = []
            for t, p in zip(times, pressures):
                results[loc['id']].append({"time": t, "pressure": p})
        
        # 3. weather_data.json として保存
        with open('weather_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False)
        print(f"SUCCESS: Saved data for {len(results)} locations.")
            
    except Exception as e:
        print(f"API REQUEST FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_weather()
