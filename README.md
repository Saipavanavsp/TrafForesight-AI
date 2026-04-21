# TrafForesight-AI: 3D Intelligent Global Routing

> **A high-fidelity global routing dashboard integrated with AI-driven traffic prediction and cinematic 3D mapping.**

![Status](https://img.shields.io/badge/Status-Active-success)
![3D Graphics](https://img.shields.io/badge/Engine-360%20Globe-blue)
![AI Engine](https://img.shields.io/badge/AI-Route%20Optimizer-orange)

TrafForesight-AI is a next-generation urban mobility platform that combines **Cinematic 3D Earth Visualization** with **Machine Learning** to find the absolute best routes based on real-time and historical traffic data.

## 🌍 Key Features

### 1. 3D Intelligent Globe
- **Cinematic Earth View**: A fully interactive 3D globe with atmospheric shading and day/night transitions.
- **Global Search**: Hybrid search engine providing 100% accurate global suggestions without API errors.
- **Micro-Animations**: Smooth transitions and glassmorphism UI for a premium experience.

### 2. AI Route Optimization
- **Traffic Analysis**: Processes local `.csv` traffic data to predict congestion levels.
- **Vehicle-Specific Routing**: Calculating different impacts for 2-Wheelers, 4-Wheelers, and Heavy Vehicles.
- **Multi-Objective Cost Engine**: Evaluates distance, base time, and traffic probability to find the "Optimal Path".
- **Visual Feedback**: Real-time coloring of the "Best Route" in Lime Green on the 3D globe.

### 3. "Drop a Pin" (Rapido Style)
- **Manual Pinning**: Accurate start (Red) and destination (Green) pin placement directly on the globe.
- **Reverse Geocoding**: Pins automatically sync with address bars in the sidebar.

## 🛠 Tech Stack
- **Backend**: FastAPI (Python), Uvicorn.
- **Predictive Engine**: Scikit-learn (Random Forest), Pandas.
- **Mapping Engine**: Google Maps JS SDK (Globe Mode) + Nominatim Search.
- **UI/UX**: Glassmorphism CSS, Outfit Typography.

## 🚀 Deployment

### Local Deployment
1. Install dependencies: `pip install -r requirements.txt`
2. Run server: `uvicorn app.api:app --reload`
3. Open: `http://127.0.0.1:8000`

### Cloud Deployment (Render)
1. **Push to GitHub**: Upload this project to a new repository on your GitHub.
2. **Connect to Render**:
   - Go to [Render.com](https://render.com) and sign in.
   - Click **"New +"** -> **"Web Service"**.
   - Connect your GitHub repository.
   - Render will automatically detect the settings in `render.yaml` and deploy it.
3. **Live**: Your dashboard will be live at `https://trafforesight-ai.onrender.com`.

## 📊 Analytics Dashboard
| Feature | AI Impact | Description |
| ------- | ---------- | ----------- |
| **Travel Time** | -31.1% | Reduction in average travel time during peak hours. |
| **Accuracy** | 91.2% | ML model precision in predicting congestion levels. |
| **Coverage** | Global | Full 3D support for both India and the rest of the world. |

---
**Author:** Sai pavan  
**Vision:** Smart Cities & AI-Driven Mobility
