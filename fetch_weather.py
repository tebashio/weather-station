import requests
import json
import time
import sys

def fetch_weather():
    print("--- 博士の気象データ収集システム 起動 ---")
    
    # 1. 観測地点リストを読み込む
    try:
        with open('locations.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)
    except Exception as e:
        print(f"エラー: locations.json の読み込みに失敗しました: {e}")
        sys.exit(1)

    def chunk_list(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    results = {}
    
    # 2. チャンク処理（Open-Meteoは一度に50地点程度まで推奨）
    for chunk in chunk_list(locations, 50):
        lats = ",".join([str(l['lat']) for l in chunk])
        lons = ",".join([str(l['lon']) for l in chunk])
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly=surface_pressure&past_days=3&forecast_days=11&timezone=Asia%2FTokyo"
        
        try:
            print(f"データ取得中: {len(chunk)} 地点...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Open-Meteoは複数地点の場合、リストを返す
            # 単一地点の場合は辞書を返すため、リストに統一して処理する
            responses = data if isinstance(data, list) else [data]
            
            for i, loc in enumerate(chunk):
                # IDをキーにして保存
                target_data = responses[i]
                hourly = target_data.get('hourly', {})
                
                times = hourly.get('time', [])
                pressures = hourly.get('surface_pressure', [])
                
                # 地点ごとのデータ配列を作成
                point_history = []
                for t, p in zip(times, pressures):
                    point_history.append({"time": t, "pressure": p})
                
                results[loc['id']] = point_history
                
        except Exception as e:
            print(f"警告: データ取得に失敗した地点があります: {e}")

        time.sleep(1) # サーバー負荷軽減

    # 3. 保存
    try:
        with open('weather_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"成功: {len(results)} 地点のデータを weather_data.json に保存しました。")
    except Exception as e:
        print(f"エラー: ファイル保存に失敗しました: {e}")

if __name__ == "__main__":
    fetch_weather()
