import requests
import json
import time
import sys

def fetch_weather():
    print("--- 気象データ同期システム起動 ---")
    
    try:
        with open('locations.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)
    except Exception as e:
        print(f"Error loading locations: {e}")
        sys.exit(1)

    results = {}
    
    # Open-Meteo API (一括取得)
    lats = ",".join([str(l['lat']) for l in locations])
    lons = ",".join([str(l['lon']) for l in locations])
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=surface_pressure&past_days=3&forecast_days=11&timezone=Asia%2FTokyo"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # 複数地点の場合はリスト、単一地点の場合は辞書が返る
        responses = data if isinstance(data, list) else [data]
        
        for i, loc in enumerate(locations):
            point_data = responses[i]
            hourly = point_data.get('hourly', {})
            times = hourly.get('time', [])
            pressures = hourly.get('surface_pressure', [])
            
            # 1地点分のデータを格納
            results[loc['id']] = []
            for t, p in zip(times, pressures):
                results[loc['id']].append({"time": t, "pressure": p})
        
        with open('weather_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False)
        print(f"完了: {len(results)} 地点のデータを保存しました。")
            
    except Exception as e:
        print(f"API Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_weather()
