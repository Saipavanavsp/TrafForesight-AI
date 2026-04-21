import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from preprocess import TrafficPreprocessor

def train_model():
    # 1. Load Dataset
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'traffic.csv')
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows of traffic data.")

    # 2. Preprocessing
    preprocessor = TrafficPreprocessor()
    X = preprocessor.transform(df)
    y = df['vehicle_count']

    # 3. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Train Random Forest (The Core ML Model)
    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # 5. Baseline Comparison (Simple Average)
    # This is critical for portfolio credibility
    y_mean = np.full(shape=y_test.shape, fill_value=y_train.mean())
    baseline_mae = mean_absolute_error(y_test, y_mean)
    
    # 6. Evaluate Model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("\n" + "="*30)
    print("      MODEL PERFORMANCE")
    print("="*30)
    print(f"Random Forest MAE:  {mae:.2f}")
    print(f"Baseline (Mean) MAE: {baseline_mae:.2f}")
    print(f"RMSE:               {rmse:.2f}")
    print(f"R² Score:           {r2:.2f}")
    print("="*30)

    # 7. Save Artifacts
    model_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(model_dir, exist_ok=True)
    with open(os.path.join(model_dir, 'rf_model.pkl'), 'wb') as f:
        pickle.dump(model, f)
    with open(os.path.join(model_dir, 'preprocessor.pkl'), 'wb') as f:
        pickle.dump(preprocessor, f)
    
    print("\nSaved artifacts to model/ directory.")
    
    return X_test, y_test, y_pred

if __name__ == "__main__":
    train_model()
