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

import pandas as pd
import io

@app.post("/api/evaluate_routes")
async def evaluate_routes(
    csv_file: UploadFile = File(...),
    routes_metadata: str = Form(...),
    vehicle_type: str = Form(...),
    day_of_week: int = Form(...),
    hour: int = Form(...),
    simulation_mode: bool = Form(False)
):
    try:
        routes = json.loads(routes_metadata)
    except json.JSONDecodeError:
        return {"error": "Invalid routes_metadata JSON"}

    # Determine simulation modifier (e.g., +30% traffic if active)
    sim_mod = 1.3 if simulation_mode else 1.0

    # Process CSV to derive dynamic baseline for anomaly detection
    baseline_volume = 250 # Default
    try:
        content = await csv_file.read()
        df_csv = pd.read_csv(io.BytesIO(content))
        if 'vehicle_count' in df_csv.columns:
            baseline_volume = float(df_csv['vehicle_count'].median())
    except Exception as e:
        print(f"CSV Parse Warning: {e}")

    # Call the upgraded model with dynamic baseline
    result = predict_traffic(day_of_week, hour, 0, 40.0, simulation_mod=sim_mod, historical_baseline=baseline_volume)
    ml_conf = result.get("confidence", 0.85)
    congestion = result.get("congestion_level", "Medium")
    
    # Apply vehicle type logic based on congestion
    base_penalty = 1.0
    if congestion in ["High", "Critical"]:
        if vehicle_type == "2-wheeler": base_penalty = 0.95
        elif vehicle_type == "4-wheeler": base_penalty = 1.6
        else: base_penalty = 2.5
    elif congestion == "Medium":
        if vehicle_type == "2-wheeler": base_penalty = 0.98
        elif vehicle_type == "4-wheeler": base_penalty = 1.2
        else: base_penalty = 1.5
         
    # Find the best route based on predicted adjusted_time
    best_route_id = 0
    min_adjusted_time = float('inf')
    best_distance = 0
    
    for r in routes:
         distance = r.get("distance", 1000)
         base_time = r.get("base_time", 100)
         adjusted_time = base_time * base_penalty
         if adjusted_time < min_adjusted_time:
             min_adjusted_time = adjusted_time
             best_route_id = r.get("id")
             best_distance = distance

    return {
        "best_route_id": best_route_id,
        "adjusted_time": min_adjusted_time,
        "distance": best_distance,
        "congestion_level": congestion,
        "predicted_traffic_volume": result.get("predicted_traffic"),
        "ml_confidence": ml_conf,
        "forecast": result.get("forecast"),
        "anomaly": result.get("anomaly"),
        "peak_window": result.get("peak_window"),
        "is_peak": result.get("is_peak"),
        "simulation_applied": result.get("simulation_applied"),
        "alert_status": result.get("alert")
    }

@app.post("/predict")
async def get_prediction(req: TrafficRequest):
    """Standardized Prediction Endpoint for Deployment Reliability."""
    result = predict_traffic(req.day_of_week, req.hour, req.weather, req.speed)
    
    if "error" in result:
        return result

    return {
        "predicted_traffic": result["predicted_traffic"],
        "congestion_level": result["congestion_level"],
        "confidence": result["confidence"],
        "forecast": result["forecast"],
        "is_peak_hour": result["is_peak"],
        "alert": result["alert"]
    }

