import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fills missing speed with mean, drops rows with missing timestamp."""
        df = df.copy()
        if 'speed' in df.columns:
            df['speed'] = df['speed'].fillna(df['speed'].mean())
        df = df.dropna(subset=['day_of_week', 'hour'])
        return df

    def extract_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Example of extraction, though our data already has day/hour."""
        # Just to demonstrate interview-level feature engineering
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        df['is_peak_hour'] = df['hour'].apply(lambda x: 1 if (7 <= x <= 9) or (16 <= x <= 18) else 0)
        return df

    def fit_transform(self, df: pd.DataFrame, features: list) -> pd.DataFrame:
        df = self.handle_missing_values(df)
        df = self.extract_time_features(df)
        df[features] = self.scaler.fit_transform(df[features])
        self.is_fitted = True
        return df

    def transform(self, df: pd.DataFrame, features: list) -> pd.DataFrame:
        df = self.handle_missing_values(df)
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        df = self.extract_time_features(df)
        df[features] = self.scaler.transform(df[features])
        return df
