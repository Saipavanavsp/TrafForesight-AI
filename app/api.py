from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from model.predict import predict_traffic

app = FastAPI(title="Traffic Prediction API")

# Serve frontend files
frontend_dir = os.path.join(base_dir, "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

class TrafficRequest(BaseModel):
    day_of_week: int
    hour: int
    weather: int
    speed: float

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/{filename}")
async def serve_root_files(filename: str):
    file_path = os.path.join(frontend_dir, filename)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

@app.post("/api/evaluate_routes")
async def evaluate_routes(
    csv_file: UploadFile = File(...),
    routes_metadata: str = Form(...),
    vehicle_type: str = Form(...),
    day_of_week: int = Form(...),
    hour: int = Form(...)
):
    try:
        routes = json.loads(routes_metadata)
    except json.JSONDecodeError:
        return {"error": "Invalid routes_metadata JSON"}

    # Mock parsing the CSV (just read a bit of it for the demo)
    content = await csv_file.read()
    if not content:
         return {"error": "Empty CSV upload"}

    # Determine weather from mock params (defaulting to clear=0, rain=1, snow=2)
    weather_condition = 0 # Default good weather
    speed = 40.0 # Default fallback speed
    
    # We call the model to get a baseline congestion scale factor
    result = predict_traffic(day_of_week, hour, weather_condition, speed)
    ml_conf = result.get("confidence", 0.85)
    congestion = result.get("congestion_level", "Medium")
    
    # Apply vehicle type logic based on congestion
    # If High congestion, 2-wheelers bypass easily, Heavy vehicles suffer heavily.
    base_penalty = 1.0
    if congestion == "High":
        if vehicle_type == "2-wheeler":
             base_penalty = 0.9  # 2 wheelers actually cut through traffic 
        elif vehicle_type == "4-wheeler":
             base_penalty = 1.4
        else:
             base_penalty = 2.0
    elif congestion == "Medium":
        if vehicle_type == "2-wheeler":
             base_penalty = 0.95
        elif vehicle_type == "4-wheeler":
             base_penalty = 1.1
        else:
             base_penalty = 1.3
    else: 
         base_penalty = 1.0 # Low traffic, everyone goes base speed
         
    # Find the best route based on predicted adjusted_time
    best_route_id = 0
    min_adjusted_time = float('inf')
    best_distance = 0
    
    for r in routes:
         distance = r.get("distance", 1000)
         base_time = r.get("base_time", 100)
         
         # Route intrinsic factors + ML penalty
         adjusted_time = base_time * base_penalty
         
         if adjusted_time < min_adjusted_time:
             min_adjusted_time = adjusted_time
             best_route_id = r.get("id")
             best_distance = distance

    weather_str = "Clear" if weather_condition == 0 else "Rainy/Snowy"

    return {
        "best_route_id": best_route_id,
        "adjusted_time": min_adjusted_time,
        "distance": best_distance,
        "congestion_penalty_factor": base_penalty,
        "weather_condition": weather_str,
        "vehicle_type": vehicle_type,
        "predicted_traffic_volume": result.get("predicted_traffic", 0),
        "ml_confidence": ml_conf
    }

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

