import requests
import json
import sys
import time

def fetch_weather():
    try:
        with open('locations.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)
        
        results = {}
        batch_size = 50  # 50地点ずつ安全にバッチ取得
        
        for i in range(0, len(locations), batch_size):
            chunk = locations[i:i + batch_size]
            lats = ",".join([str(loc['lat']) for loc in chunk])
            lons = ",".join([str(loc['lon']) for loc in chunk])
            
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=surface_pressure&past_days=3&forecast_days=11&timezone=Asia%2FTokyo"
            
            print(f"Fetching batch {i // batch_size + 1} ({len(chunk)} locations)...")
            response = requests.get(url, timeout=60)
            
            if response.status_code != 200:
                print(f"API Error ({response.status_code}): {response.text}")
                continue
                
            data = response.json()
            responses = data if isinstance(data, list) else [data]
            
            for idx, loc in enumerate(chunk):
                if idx < len(responses):
                    hourly = responses[idx].get('hourly', {})
                    times = hourly.get('time', [])
                    pressures = hourly.get('surface_pressure', [])
                    results[loc['id']] = [{"time": t, "pressure": p} for t, p in zip(times, pressures)]
            
            time.sleep(1) # APIに負荷をかけないよう1秒待機
        
        with open('weather_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False)
            
        print(f"Successfully synced {len(results)} locations to weather_data.json.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_weather()
