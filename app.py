from flask import Flask, render_template, request
from model import predict_glacier_area, predict_temperature
from satellite import get_satellite_data
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    risk_level = None
    chart_data = []
    temp_chart_data = []
    image_file = 'static/default.jpg'
    target_year = None
    show_popup = False

    if request.method == 'POST':
        try:
            lat = float(request.form['latitude'])
            lon = float(request.form['longitude'])
            target_year = int(request.form['year'])

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
                          show_popup=show_popup)

if __name__ == '__main__':
    app.run(debug=True)
