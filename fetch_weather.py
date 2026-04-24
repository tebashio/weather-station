import requests
import json
import os

# 1. 観測地点リストを読み込む
with open('locations.json', 'r') as f:
    locations = json.load(f)

# 2. Open-MeteoのURLを組み立てる
lats = ",".join([str(l['lat']) for l in locations])
lons = ",".join([str(l['lon']) for l in locations])

url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=surface_pressure&past_days=3&forecast_days=11&timezone=Asia%2FTokyo"

# 3. データを取得する
response = requests.get(url)
data = response.json()

# 4. データを整理して保存する
results = {}
# Open-Meteoの一括リクエストは、配列でデータが返ってくるので順番に紐付けます
for i, loc in enumerate(locations):
    city_data = data[i] if isinstance(data, list) else data
    
    # 複数地点の場合はdata自体がリストではなく、各項目がリストになる
    hourly = data['hourly'] if len(locations) == 1 else data[i]['hourly']
    
    results[loc['id']] = []
    for t, p in zip(hourly['time'], hourly['surface_pressure']):
        results[loc['id']].append({"time": t, "pressure": p})

with open('weather_data.json', 'w') as f:
    json.dump(results, f)
