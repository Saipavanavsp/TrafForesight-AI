import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class TrafficPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def transform(self, df, features=['speed']):
        df = df.copy()
        
        # 1. Cyclic Encoding for Time Features (Professional Approach)
        # Hour (24h)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Day of Week (7 days)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # 2. Add Binary Flags
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        df['is_peak_hour'] = df['hour'].apply(lambda x: 1 if (8 <= x <= 10) or (17 <= x <= 20) else 0)
        
        # 3. Handle Missing Values
        df = df.fillna(df.median(numeric_only=True))
        
        # 4. Scaling
        if not self.is_fitted:
            self.scaler.fit(df[features])
            self.is_fitted = True
            
        df[features] = self.scaler.transform(df[features])
        
        # Final Feature selection for Model
        return df[['day_of_week', 'hour', 'weather', 'speed', 'is_weekend', 'is_peak_hour']]

if __name__ == "__main__":
    # Test Preprocessor
    test_data = pd.DataFrame({'day_of_week': [0, 6], 'hour': [8, 18], 'weather': [1, 2], 'speed': [40, 20]})
    prep = TrafficPreprocessor()
    processed = prep.transform(test_data)
    print("Preprocessed Features Sample:")
    print(processed.head())
