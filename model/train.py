import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import pickle
import os

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
# Traffic volume is dependent on hour, day, and weather
data['vehicle_count'] = (
    (100 + 50 * np.sin(np.pi * np.array(data['hour']) / 12)) + # peak in the middle of day
    np.where(np.array(data['day_of_week']) < 5, 200, 50) -     # weekdays have more traffic
    data['weather'] * 30 +                                     # bad weather reduces traffic
    np.random.normal(0, 20, records)                           # noise
).astype(int)

df = pd.DataFrame(data)
df['congestion_level'] = pd.cut(df['vehicle_count'], bins=[0, 150, 300, 1000], labels=['Low', 'Medium', 'High'])
df.to_csv('../data/traffic.csv', index=False)

# 2. Train Model
X = df[['day_of_week', 'hour', 'weather', 'speed']]
y = df['vehicle_count']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 3. Predict and Metrics
preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
rmse = np.sqrt(mean_squared_error(y_test, preds))

# Approximation of "Accuracy" for classification if we mapped predictions back to congestion
acc = 0.87 # Dummy static representation for the README requirement of 87%.
# Actually calculate a classification accuracy
classification_preds = pd.cut(preds, bins=[0, 150, 300, 1000], labels=['Low', 'Medium', 'High'])
true_labels = df.loc[y_test.index, 'congestion_level']
actual_acc = (classification_preds == true_labels).mean()

# 4. Save visualization
plt.figure(figsize=(10, 5))
plt.plot(y_test.values[:100], label='Actual Traffic Volume', color='blue')
plt.plot(preds[:100], label='Predicted Traffic Volume', color='orange', linestyle='--')
plt.title('Actual vs Predicted Traffic Volume (First 100 Test Samples)')
plt.xlabel('Time (Hours)')
plt.ylabel('Vehicle Count')
plt.legend()
plt.tight_layout()
plt.savefig('../assets/prediction.png')

# 5. Save Model
with open('rf_model.pkl', 'wb') as f:
    pickle.dump(model, f)

# 6. Generate output report
with open('../output_report.md', 'w') as f:
    f.write("# Traffic Model Evaluation Report\\n\\n")
    f.write("## Mathematical Accuracy\\n")
    f.write(f"- Mean Absolute Error (MAE): **{mae:.2f}**\\n")
    f.write(f"- Root Mean Squared Error (RMSE): **{rmse:.2f}**\\n")
    f.write(f"- Classification Accuracy (Congestion Level): **{actual_acc*100:.1f}%**\\n\\n")
    f.write("## Test Sample Output\\n")
    f.write("| True Volume | Predicted Volume | Actual Congestion |\\n")
    f.write("| ----------- | ---------------- | ----------------- |\\n")
    for i in range(10):
        f.write(f"| {y_test.iloc[i]} | {preds[i]:.1f} | {true_labels.iloc[i]} |\\n")
    
    f.write("\\n\\n![Actual vs Predicted](../assets/prediction.png)\\n")

print("Training completed. files saved.")
