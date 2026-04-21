import pickle
import pandas as pd
import numpy as np
import json
import os
import sys

# Ensure the model directory is in path for unpickling preprocess module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def predict_traffic(day_of_week: int, hour: int, weather: int, speed: float, simulation_mod=1.0, historical_baseline=250):
    """
    Enhanced Prediction Engine: 
    Supports 3D Globe, Multi-step Forecast, Anomaly Detection & Scenarios
    """
    model_path = 'model/rf_model.pkl'
    preprocessor_path = 'model/preprocessor.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        return {"error": "Model files missing."}

    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(preprocessor_path, 'rb') as f:
        preprocessor = pickle.load(f)

    # Core Prediction Function
    def get_single_pred(d, h, w, s):
        df = pd.DataFrame([{'day_of_week': d, 'hour': h % 24, 'weather': w, 'speed': s}])
        df_processed = preprocessor.transform(df, features=['speed'])
        X = df_processed[['day_of_week', 'hour', 'weather', 'speed', 'is_weekend', 'is_peak_hour']]
        
        all_tree_preds = np.array([tree.predict(X.values) for tree in model.estimators_])
        avg_pred = np.mean(all_tree_preds) * simulation_mod  # Apply "What-if" Simulation modifier
        std_pred = np.std(all_tree_preds)
        confidence = max(0, min(1, 1 - (std_pred / (avg_pred + 1e-6))))
        
        return int(avg_pred), round(float(confidence), 2)

    # 1. Primary Prediction
    curr_pred, confidence = get_single_pred(day_of_week, hour, weather, speed)

    # 2. Multi-step Forecasting (t+1h, t+3h, t+6h)
    forecast = {
        "t+1h": get_single_pred(day_of_week, hour + 1, weather, speed)[0],
        "t+3h": get_single_pred(day_of_week, hour + 3, weather, speed)[0],
        "t+6h": get_single_pred(day_of_week, hour + 6, weather, speed)[0]
    }

    # 3. Congestion Classification (Refined)
    if curr_pred > 400: status = "Critical"
    elif curr_pred > 300: status = "High"
    elif curr_pred > 150: status = "Medium"
    else: status = "Low"

    # 4. Anomaly Detection (Dynamic Baseline Comparison)
    # Compares current prediction vs. historical median derived from CSV
    historical_avg = historical_baseline 
    is_anomaly = curr_pred > (historical_avg * 1.6)
    anomaly_reason = f"Volume {int(((curr_pred/historical_avg)-1)*100)}% above baseline" if is_anomaly else "None"

    # 5. Peak Hour Detection
    is_peak = (8 <= hour <= 10) or (17 <= hour <= 20)
    peak_window = "8:00-10:00 AM" if (8 <= hour <= 10) else ("5:00-8:00 PM" if (17 <= hour <= 20) else "Off-Peak")

    return {
        "predicted_traffic": curr_pred,
        "congestion_level": status,
        "confidence": confidence,
        "forecast": forecast,
        "peak_window": peak_window,
        "is_peak": is_peak,
        "anomaly": {
            "is_detected": is_anomaly,
            "reason": anomaly_reason
        },
        "simulation_applied": simulation_mod > 1.0,
        "alert": "RED_ALERT" if status == "Critical" or is_anomaly else "NORMAL"
    }

if __name__ == "__main__":
    print(json.dumps(predict_traffic(3, 18, 0, 45.0), indent=2))
