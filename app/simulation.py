import time
import random
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.predict import predict_traffic

def run_simulation(steps=10):
    print("--- Starting Real-Time Traffic Simulation ---")
    print("Simulating live feed from intersection sensors...\n")
    
    for i in range(steps):
        # Generate random "current" conditions
        hour = (time.localtime().tm_hour + i) % 24
        day = time.localtime().tm_wday # 0-6
        weather = random.choice([0, 1, 2])
        speed = random.uniform(20, 60)
        
        result = predict_traffic(day, hour, weather, speed)
        
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] Sensor Input -> Hour: {hour}, Weather: {weather}, Speed: {speed:.1f} km/h")
        print(f"           Prediction -> Volume: {result['predicted_traffic']}, Congestion: {result['congestion_level']}, Confidence: {result['confidence']*100}%")
        
        if result['alert'] == "CRITICAL":
            print("           !!! ALERT: High Congestion Expected !!!")
            
        print("-" * 50)
        time.sleep(2) # Fast forward simulation

if __name__ == "__main__":
    run_simulation()
