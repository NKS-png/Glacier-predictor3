from sklearn.linear_model import LinearRegression
import numpy as np

# Train a dummy model using random logic
def predict_glacier_area(features):
    predictions = []
    for year, temp, surface_temp in features:
        # More realistic melting model
        base = 50 - (temp * 0.7) - (surface_temp * 0.3) - ((year - 2025) * 1.5)
        predictions.append(max(base, 0))
    return predictions

def predict_temperature(features):
    predictions = []
    for year, base_temp in features:
        # Simulate a gradual temperature increase
        increase = (year - 2025) * 0.05
        predictions.append(base_temp + increase)
    return predictions
