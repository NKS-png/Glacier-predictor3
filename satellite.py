import requests

def get_satellite_data(lat, lon, date_str):
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters=T2M,TS&community=RE&longitude={lon}&latitude={lat}&format=JSON"
        f"&start={date_str}&end={date_str}"
    )

    print(f"[INFO] Fetching NASA API data for {date_str}")
    print(f"[URL] {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        record = data['properties']['parameter']
        temperature = record.get('T2M', {}).get(date_str)
        surface_temp = record.get('TS', {}).get(date_str)

        print(f"[DATA] T2M: {temperature}, TS: {surface_temp}")

        if temperature in [None, -999] or surface_temp in [None, -999]:
            print("[WARN] Missing or invalid satellite data")
            return None, None

        return temperature, surface_temp

    except Exception as e:
        print(f"[ERROR] Satellite fetch failed: {e}")
        return None, None
