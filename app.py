from flask import Flask, render_template, request
from model import predict_glacier_area, predict_temperature
from satellite import get_satellite_data
from datetime import datetime, timedelta
import requests
from io import BytesIO
from PIL import Image
import base64
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # ... [all your existing logic stays the same] ...
    return render_template('index.html',
                           prediction=prediction,
                           risk=risk_level,
                           chart_data=chart_data,
                           temp_chart_data=temp_chart_data,
                           image_file=image_file,
                           target_year=target_year,
                           show_popup=show_popup,
                           image_data=image_data,
                           image_data_2025=image_data_2025,
                           error_message=error_message,
                           info_message=info_message)


    if request.method == 'POST':
        try:
            lat = 28.5  # Fixed Himalaya latitude
            lon = 85.0  # Fixed Himalaya longitude
            target_year = int(request.form['year'])
            current_year = datetime.now().year

            def get_image_data(year):
                url = f"https://services.sentinel-hub.com/ogc/wms/44a4a2ff-fbc0-4c37-b7fa-f52fa99cbdb7/?REQUEST=GetMap&BBOX={lat-0.05},{lon-0.05},{lat+0.05},{lon+0.05}&LAYERS=TRUE_COLOR&WIDTH=256&HEIGHT=256&FORMAT=image/jpeg&TIME={year}-01-01/{year}-12-31&SRS=EPSG:4326"
                response = requests.get(url)
                if response.status_code != 200 or not response.content or len(response.content) < 100:
                    return None
                image = Image.open(BytesIO(response.content))
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                return base64.b64encode(buffered.getvalue()).decode("utf-8")

            try:
                satellite_year = min(target_year, current_year)
                image_data = get_image_data(satellite_year)

                if target_year > current_year:
                    image_data_2025 = get_image_data(current_year)
                    info_message = f"Comparison: {current_year} (left) vs. {target_year} prediction (right)."

                if not image_data:
                    raise Exception("Failed to fetch satellite image.")

            except Exception as e:
                image_data = None
                image_data_2025 = None
                error_message = f"Failed to fetch satellite image: {str(e)}"
                print(f"Image fetch failed: {e}")

            # Try yesterday's date, fallback to -2 if fails
            for days_ago in range(1, 6):
                date_obj = datetime.today() - timedelta(days=days_ago)
                date_str = date_obj.strftime('%Y%m%d')
                temp, snow = get_satellite_data(lat, lon, date_str)
                if temp is not None:
                    break
            else:
                temp, snow = None, None

            if temp is not None:
                current_year = datetime.now().year
                years = list(range(current_year, target_year + 1))
                
                # Glacier area prediction
                predicted_areas = predict_glacier_area([[y, temp, snow] for y in years])
                predicted_areas = [round(a, 2) for a in predicted_areas]
                prediction = predicted_areas[-1]
                chart_data = list(zip(years, predicted_areas))

                # Temperature prediction
                predicted_temps = predict_temperature([[y, temp] for y in years])
                predicted_temps = [round(t, 2) for t in predicted_temps]
                temp_chart_data = list(zip(years, predicted_temps))

                # Risk message and dynamic image
                if prediction > 20:
                    risk_level = "🟢 Low | Glacier is relatively stable."
                    image_file = 'static/low_risk.jpg'
                elif prediction > 10:
                    risk_level = "🟠 Medium | Noticeable melting, monitor closely."
                    image_file = 'static/medium_risk.jpg'
                else:
                    risk_level = "🔴 High | Glacier area is critically low."
                    image_file = 'static/high_risk.jpg'
            else:
                risk_level = "⚠️ Not a glacier. Please pick a different location."
                show_popup = True

        except Exception as e:
            print(f"[ERROR] Form processing failed: {e}")
            risk_level = f"❌ Error occurred: {str(e)}"

    return render_template('index.html',
                           prediction=prediction,
                           risk=risk_level,
                           chart_data=chart_data,
                           temp_chart_data=temp_chart_data,
                           image_file=image_file,
                           target_year=target_year,
                           show_popup=show_popup,
                           image_data=image_data,
                           image_data_2025=image_data_2025,
                           error_message=error_message,
                           info_message=info_message)

