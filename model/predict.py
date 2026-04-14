import pickle
import pandas as pd
import numpy as np
import json
import os
import sys

# Ensure the model directory is in path for unpickling preprocess module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def predict_traffic(day_of_week: int, hour: int, weather: int, speed: float):
    # Paths
    model_path = 'model/rf_model.pkl'
    preprocessor_path = 'model/preprocessor.pkl'
    
    # Handle missing files
    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        return {"error": "Model or Preprocessor files not found. Please run train.py first."}

    # Load artifacts
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(preprocessor_path, 'rb') as f:
        preprocessor = pickle.load(f)
        
    # Input Validation / Edge Case handling
    if not (0 <= day_of_week <= 6): day_of_week = 0
    if not (0 <= hour <= 23): hour = 12
    if weather not in [0, 1, 2]: weather = 0
    if speed < 0: speed = 0

    # Create DataFrame
    df = pd.DataFrame([{
        'day_of_week': day_of_week,
        'hour': hour,
        'weather': weather,
        'speed': speed
    }])
    
    # Preprocess
    try:
        df_processed = preprocessor.transform(df, features=['speed'])
        X = df_processed[['day_of_week', 'hour', 'weather', 'speed', 'is_weekend', 'is_peak_hour']]
    except Exception as e:
        return {"error": f"Preprocessing failed: {str(e)}"}
    
    # Prediction with Confidence (STD of tree predictions)
    all_tree_preds = np.array([tree.predict(X.values) for tree in model.estimators_])
    avg_pred = np.mean(all_tree_preds)
    std_pred = np.std(all_tree_preds)
    
    # Confidence Score: 1 - (Normalized STD / Mean) -> Simplified heuristic
    confidence = max(0, min(1, 1 - (std_pred / (avg_pred + 1e-6))))
    
    congestion = 'Low'
    if avg_pred > 300:
        congestion = 'High'
    elif avg_pred > 150:
        congestion = 'Medium'
        
    return {
        "predicted_traffic": int(avg_pred),
        "congestion_level": congestion,
        "confidence": round(float(confidence), 2),
        "alert": "CRITICAL" if avg_pred > 400 else "NONE"
    }

if __name__ == "__main__":
    # Test sample
    result = predict_traffic(3, 18, 0, 45.0)
    print(json.dumps(result, indent=2))

