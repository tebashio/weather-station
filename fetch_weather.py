import requests
import json
import sys

def fetch_weather():
    try:
        with open('locations.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)
        
        # 142地点の緯度経度をカンマ区切りで結合
        lats = ",".join([str(l['lat']) for l in locations])
        lons = ",".join([str(l['lon']) for l in locations])
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=surface_pressure&past_days=3&forecast_days=11&timezone=Asia%2FTokyo"
        
        response = requests.get(url, timeout=60)
        data = response.json()
        
        # リクエスト数に応じたレスポンス形式の正規化
        responses = data if isinstance(data, list) else [data]
        
        results = {}
        for i, loc in enumerate(locations):
            hourly = responses[i].get('hourly', {})
            # ID (loc_XXX) をキーにして気圧履歴を保存
            results[loc['id']] = [{"time": t, "pressure": p} for t, p in zip(hourly.get('time', []), hourly.get('surface_pressure', []))]
        
        with open('weather_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False)
        print(f"Synced {len(results)} locations.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_weather()
