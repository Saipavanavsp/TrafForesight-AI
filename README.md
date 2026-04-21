# TrafForesight-AI: Spatio-Temporal Route Intelligence & Predictive Engine 🚥🌍🚀

**TrafForesight-AI** is a professional-grade, multi-layered traffic predictive framework developed for the **VIT Capstone Project**. It optimizes urban mobility and emergency response using advanced Ensemble Learning and cinematic 3D visualization.

---

## 🎯 Project Overview
The core objective of **TrafForesight-AI** is to bridge the gap between static navigation and dynamic urban reality. By leveraging a **Random Forest Predictive Engine**, the system anticipates congestion before it occurs, providing a 31.1% more resilient routing path compared to traditional heuristics.

---

## 🏆 Academic Excellence (Capstone Spotlight)
This project was designed to meet the high expectations of the **Vellore Institute of Technology (VIT)** Capstone requirements:
- **Novelty:** Implementation of an AI-Weighted Penalty Function for routing.
- **Robustness:** Includes a full suite of Unit Tests and Anomaly Detection.
- **Accuracy:** Achieved an **R² score of 0.89** with a **67.6% reduction in MAE** over baseline.
- **Documentation:** Full technical report available in [/docs/TECHNICAL_REPORT.md](docs/TECHNICAL_REPORT.md).

---

## 🎨 Dashboard Architecture & High Fidelity UI
The frontend is a bespoke **Glassmorphism-styled Dashboard**:
1.  **3D Globe Engine**: Built using the **Google Maps JavaScript Beta API**, enabling full 3D Earth tilt, rotation, and cinematic globe fly-ins.
2.  **Simulation Engine**: "What-if" scenarios for **Peak Load (+30% traffic)** allow stress tests on urban infrastructure.
3.  **Real-Time Analytics**: Seamless integration with **Chart.js** to visualize predicted traffic volumes ($T+1, T+3, T+6$ hours).

---

## 🧠 Technical Foundation

### 1. Feature Engineering
We implement **Cyclic Trigonometric Encoding** for temporal features to ensure the model understands time continuity:
$$x_{sin} = \sin\left(\frac{2\pi \cdot x}{Max\_x}\right)$$

### 2. Predictive Engine
A **Random Forest Regressor** with 100 estimators serves as the backbone, handling non-linear traffic patterns and providing a confidence interval for every prediction.

### 3. Anomaly Detection
The system automatically identifies volume spikes by comparing predictions against a **Dynamic Historical Median** derived from regional data.

---

## 🚀 Deployment & Installation

### 1. Local Setup
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Launch the Server**:
    ```bash
    uvicorn app.api:app --reload
    ```
3.  **Access**: Navigate to `http://127.0.0.1:8000/`.

### 2. Cloud Configuration
Pre-configured for **Render.com** with `render.yaml` and `Procfile`.

---

## 📂 Project Structure
```text
TrafForesight-AI/
├── app/               # FastAPI Backend & Intelligence Endpoints
├── data/              # Traffic datasets (CSV)
├── docs/              # Professional Technical Reports (Capstone)
├── frontend/          # 3D Dashboards (HTML/CSS/JS)
├── model/             # ML Pipeline (Preprocess, Train, Eval)
├── assets/            # Model plots & Architecture diagrams
└── tests/             # Unit tests for reliability
```

---
*Developed for the VIT Capstone Project 2026.*
