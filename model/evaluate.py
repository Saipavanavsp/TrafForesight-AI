import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from train import train_model

def generate_evaluation_report():
    # 1. Run training to get test results
    X_test, y_test, y_pred = train_model()
    
    # 2. Calculate Final Metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # 3. Create Visualization: Actual vs Predicted
    plt.figure(figsize=(10, 6))
    sns.set_style("darkgrid")
    
    # Scatter plot
    plt.scatter(y_test, y_pred, alpha=0.5, color='#3b82f6', label='Predictions')
    
    # Perfect prediction line
    line_coords = [y_test.min(), y_test.max()]
    plt.plot(line_coords, line_coords, '--', color='#ef4444', linewidth=2, label='Perfect Fit')
    
    plt.title(f'TrafForesight-AI: Actual vs Predicted Traffic Volume\n(R² Score: {r2:.2f})', fontsize=14)
    plt.xlabel('Actual Volume (vehicles/hr)', fontsize=12)
    plt.ylabel('AI Predicted Volume', fontsize=12)
    plt.legend()
    
    # Save graph to assets
    model_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(os.path.dirname(model_dir), 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    graph_path = os.path.join(assets_dir, 'actual_vs_predicted.png')
    plt.savefig(graph_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nEvaluation Complete.")
    print(f"Graph saved to: {graph_path}")
    
    # Create a small markdown report snippet
    report = f"""
### Model Performance Metrics
- **Mean Absolute Error (MAE):** {mae:.2f}
- **Root Mean Squared Error (RMSE):** {rmse:.2f}
- **R² Score:** {r2:.2f}
    """
    
    report_path = os.path.join(model_dir, 'eval_report.md')
    with open(report_path, 'w') as f:
        f.write(report)
    
    return report

if __name__ == "__main__":
    generate_evaluation_report()
