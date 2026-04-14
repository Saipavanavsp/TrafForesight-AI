import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import pickle
import os

from preprocess import DataPreprocessor

# 1. Generate Dataset
np.random.seed(42)
days = 30
hours = 24
records = days * hours

data = {
    'timestamp': pd.date_range(start='2026-03-01', periods=records, freq='h'),
    'day_of_week': [d % 7 for d in range(records)],
    'hour': [h % 24 for h in range(records)],
    'weather': np.random.choice([0, 1, 2], records), # 0: clear, 1: rain, 2: snow
    'speed': np.random.uniform(10, 80, records)
}
data['vehicle_count'] = (
    (100 + 50 * np.sin(np.pi * np.array(data['hour']) / 12)) +
    np.where(np.array(data['day_of_week']) < 5, 200, 50) -
    data['weather'] * 30 +
    np.random.normal(0, 20, records)
).astype(int)

df = pd.DataFrame(data)
df['congestion_level'] = pd.cut(df['vehicle_count'], bins=[0, 150, 300, 1000], labels=['Low', 'Medium', 'High'])
df.to_csv('../data/traffic.csv', index=False)

# 2. Preprocess
preprocessor = DataPreprocessor()
df_processed = preprocessor.fit_transform(df, features=['speed'])

X = df_processed[['day_of_week', 'hour', 'weather', 'speed', 'is_weekend', 'is_peak_hour']]
y = df_processed['vehicle_count']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# 3. Train Models
# Random Forest
model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
model_rf.fit(X_train, y_train)
preds_rf = model_rf.predict(X_test)

# Linear Regression (Comparison)
model_lr = LinearRegression()
model_lr.fit(X_train, y_train)
preds_lr = model_lr.predict(X_test)

# Baseline (Mean of Train set)
baseline_pred = np.full_like(y_test, y_train.mean())

# Metrics Comparison
mae_rf = mean_absolute_error(y_test, preds_rf)
rmse_rf = np.sqrt(mean_squared_error(y_test, preds_rf))

mae_lr = mean_absolute_error(y_test, preds_lr)
rmse_lr = np.sqrt(mean_squared_error(y_test, preds_lr))

mae_base = mean_absolute_error(y_test, baseline_pred)
rmse_base = np.sqrt(mean_squared_error(y_test, baseline_pred))

# 4. Save visualization (Prediction)
plt.figure(figsize=(10, 5))
plt.plot(y_test.values[:100], label='Actual Traffic Volume', color='blue')
plt.plot(baseline_pred[:100], label='Baseline (Average)', color='gray', linestyle=':')
plt.plot(preds_rf[:100], label='Predicted Traffic Volume (RF)', color='orange', linestyle='--')
plt.title('Time-Series Forecasting: Actual vs Predicted Traffic Volume')
plt.xlabel('Time (Hours)')
plt.ylabel('Vehicle Count')
plt.legend()
plt.tight_layout()
plt.savefig('../assets/prediction.png')

# 5. Feature Importance
importance = model_rf.feature_importances_
features = X.columns
plt.figure(figsize=(8, 4))
sns.barplot(x=importance, y=features, palette="viridis")
plt.title('Feature Importance (Random Forest)')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('../assets/feature_importance.png')

# 6. Congestion Heatmap
plt.figure(figsize=(10, 6))
heatmap_data = df.pivot_table(values='vehicle_count', index='day_of_week', columns='hour', aggfunc='mean')
sns.heatmap(heatmap_data, cmap="YlOrRd", annot=False)
plt.title('Congestion Heatmap (Vehicle Count avg by Day/Hour)')
plt.ylabel('Day of Week (0=Mon)')
plt.xlabel('Hour of Day')
plt.tight_layout()
plt.savefig('../assets/heatmap.png')

# 7. Save Model and Preprocessor
with open('rf_model.pkl', 'wb') as f:
    pickle.dump(model_rf, f)
with open('preprocessor.pkl', 'wb') as f:
    pickle.dump(preprocessor, f)

# 8. Generate output report
with open('../output_report.md', 'w') as f:
    f.write("# Traffic Model Evaluation & Comparison\\n\\n")
    
    f.write("## 1. Model vs Baseline Comparison\\n")
    f.write("| Model | MAE | RMSE |\\n")
    f.write("| ----- | --- | ---- |\\n")
    f.write(f"| **Baseline (Mean)** | {mae_base:.2f} | {rmse_base:.2f} |\\n")
    f.write(f"| **Linear Regression** | {mae_lr:.2f} | {rmse_lr:.2f} |\\n")
    f.write(f"| **Random Forest (Final)** | **{mae_rf:.2f}** | **{rmse_rf:.2f}** |\\n\\n")

    f.write("## 2. Feature Importance\\n")
    f.write("The Random Forest model identified spatial and temporal structures inside the data:\\n")
    f.write("![Feature Importance](../assets/feature_importance.png)\\n\\n")
    
    f.write("## 3. Heatmap Visualization\\n")
    f.write("Macroscopic view of congestion buildup using time-series aggregations:\\n")
    f.write("![Congestion Heatmap](../assets/heatmap.png)\\n\\n")
    
    f.write("## 4. Time-Series Predictor\\n")
    f.write("![Actual vs Predicted vs Baseline](../assets/prediction.png)\\n")

print("Training + Advanced visuals generated successfully.")
