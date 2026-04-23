import requests
import json

# Mocking the frontend request
url = "http://127.0.0.1:8000/api/evaluate_routes"
routes = [
    {"id": 0, "base_time": 3600, "distance": 50000}, # Route 1
    {"id": 1, "base_time": 4200, "distance": 45000}  # Route 2
]

data = {
    "routes_metadata": json.dumps(routes),
    "vehicle_type": "4-wheeler",
    "day_of_week": 3,
    "hour": 18,
    "simulation_mode": "true"
}

try:
    # We don't send a CSV, testing the "automatic fallback" I added
    response = requests.post(url, data=data)
    print("API Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
