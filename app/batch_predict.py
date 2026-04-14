import pandas as pd
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.predict import predict_traffic

def batch_process(input_csv="data/traffic.csv", output_json="data/batch_predictions.json"):
    print(f"--- Running Batch Prediction Engine ---")
    if not os.path.exists(input_csv):
        print("Error: Input data not found.")
        return

    df = pd.read_csv(input_csv).head(50) # Process first 50 records as batch
    results = []
    
    print(f"Processing {len(df)} records in batch...")
    for _, row in df.iterrows():
        pred = predict_traffic(
            int(row['day_of_week']), 
            int(row['hour']), 
            int(row['weather']), 
            float(row['speed'])
        )
        results.append({
            "timestamp": str(row['timestamp']),
            "predicted_volume": pred.get("predicted_traffic"),
            "confidence": pred.get("confidence")
        })
    
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Batch processing complete. Results saved to {output_json}")

if __name__ == "__main__":
    batch_process()
