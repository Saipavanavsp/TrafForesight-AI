import pickle
import pandas as pd
import json

def predict_traffic(day_of_week: int, hour: int, weather: int, speed: float):
    # Load model
    with open('model/rf_model.pkl', 'rb') as f:
        model = pickle.load(f)
        
    df = pd.DataFrame([{
        'day_of_week': day_of_week,
        'hour': hour,
        'weather': weather,
        'speed': speed
    }])
    
    pred = model.predict(df)[0]
    
    congestion = 'Low'
    if pred > 300:
        congestion = 'High'
    elif pred > 150:
        congestion = 'Medium'
        
    return {
        "predicted_traffic": int(pred),
        "congestion_level": congestion
    }

if __name__ == "__main__":
    result = predict_traffic(3, 18, 0, 45.0)
    print(json.dumps(result, indent=2))
