from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.predict import predict_traffic

app = FastAPI(title="Traffic Prediction API")

class TrafficRequest(BaseModel):
    day_of_week: int
    hour: int
    weather: int
    speed: float

@app.post("/predict")
def get_prediction(req: TrafficRequest):
    result = predict_traffic(req.day_of_week, req.hour, req.weather, req.speed)
    
    if "error" in result:
        return result

    return {
        "timestamp": "2026-04-14 18:00",
        "predicted_traffic": result["predicted_traffic"],
        "congestion_level": result["congestion_level"],
        "confidence": result["confidence"],
        "alert_status": result["alert"]
    }

