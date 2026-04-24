import requests
import json
import time

# 1. 観測地点リストを読み込む
with open('locations.json', 'r', encoding='utf-8') as f:
    locations = json.load(f)

def chunk_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

results = {}
# 2. 50地点ずつに分けて取得（チャンク処理）
for chunk in chunk_list(locations, 50):
    lats = ",".join([str(l['lat']) for l in chunk])
    lons = ",".join([str(l['lon']) for l in chunk])
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=surface_pressure&past_days=3&forecast_days=11&timezone=Asia%2FTokyo"
    
    response = requests.get(url)
    data = response.json()
    
    # 3. 取得したデータを一つのresults辞書にマージする
    # 地点が1つの場合と複数の場合でレスポンス形式が違うので対応
    for i, loc in enumerate(chunk):
        hourly_data = data[i]['hourly'] if isinstance(data, list) else data['hourly']
        # 地点数が多い場合はdata自体がリスト、少ない(1地点)なら辞書になるOpen-Meteoの仕様対策
        if len(chunk) > 1:
            hourly_data = data[i]['hourly']
        else:
            hourly_data = data['hourly']

        results[loc['id']] = []
        for t, p in zip(hourly_data['time'], hourly_data['surface_pressure']):
            results[loc['id']].append({"time": t, "pressure": p})
    
    # APIへの負荷軽減のため、少しだけ休憩（マナー）
    time.sleep(1)

# 4. 全地点分がまとまった一つのファイルとして保存
with open('weather_data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False)
