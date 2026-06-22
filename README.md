# NBA 3-Point Shot Predictor

An AI-powered web application that predicts whether an NBA 3-point shot will be made or missed using machine learning (XGBoost).

**Live Demo**: Visit `http://localhost:3000` after starting the application

## 📊 Project Status

- ✅ **ML Pipeline Complete** (98.9% accuracy, 99% F1 score, 99.3% ROC-AUC)
- ✅ **FastAPI Backend** (REST API with single/batch predictions)
- ✅ **React Frontend** (Interactive UI dashboard)
- ✅ **Docker Support** (Containerized for easy deployment)
- ✅ **Model Metrics** (XGBoost trained on 904 NBA shots from 3 players, 2 seasons)

## 🏀 Dataset

- **Players**: Stephen Curry, Klay Thompson, Damian Lillard
- **Seasons**: 2022-23, 2023-24
- **Rows**: 4,266 balanced shots (50% made, 50% synthesized misses)
- **Training**: 904 rows after cleaning, 80/20 train/test split

## 🎯 Features

### Model
- **Algorithm**: XGBoost Classifier
- **Input Features**: Shot distance, zone, period, time, defender distance, dribbles, touch time, location
- **Engineered Features**: gameTimeRemaining, courtDistance, lateGameShot, cornerThree
- **Output**: Prediction (Made/Missed) + Probability (0-1)

### Web Application
1. **Single Shot Prediction**: Enter shot parameters and get instant prediction
2. **Batch Predictions**: Upload CSV with multiple shots for bulk analysis
3. **Model Dashboard**: View real-time model performance metrics
4. **Responsive Design**: Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Option 1: Docker (Recommended)

**Requirements**: Docker and Docker Compose installed

```bash
# Navigate to project root
cd nba-3point-predictor

# Start both backend and frontend
docker-compose up

# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Requirements**: Python 3.11+, Node.js 16+ (optional for advanced frontend dev)

#### 1. Setup Backend

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Serve Frontend

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Start simple HTTP server (Python 3)
python -m http.server 3000

# Or use Node.js http-server
npm install -g http-server
http-server -p 3000
```

#### 3. Access Application

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📡 API Documentation

### FastAPI Interactive Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

#### Health Check
```bash
GET /
```

#### Single Shot Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "shotDistance": 25,
    "shotZone": "Above the Break 3",
    "period": 2,
    "minutesRemaining": 5,
    "secondsRemaining": 30,
    "shotClock": 10,
    "defenderDistance": 5,
    "dribbles": 2,
    "touchTime": 1.5,
    "locationX": 50,
    "locationY": 250
  }'
```

**Response**:
```json
{
  "prediction": "Missed",
  "probability": 0.0556,
  "input_params": { ... }
}
```

#### Batch Predictions (CSV Upload)
```bash
curl -X POST "http://localhost:8000/predict-batch" \
  -F "file=@shots.csv"
```

**CSV Format** (required columns):
```
shotDistance,shotZone,period,minutesRemaining,secondsRemaining,shotClock,defenderDistance,dribbles,touchTime,locationX,locationY
25,Above the Break 3,2,5,30,10,5,2,1.5,50,250
20,Left Corner 3,1,10,15,15,8,1,0.8,-20,85
```

#### Model Info
```bash
curl "http://localhost:8000/model-info"
```

**Response**:
```json
{
  "model_type": "XGBoost",
  "accuracy": 0.9890,
  "f1_score": 0.9904,
  "roc_auc": 0.9930,
  "training_rows": 904,
  "positive_rate": 0.5664
}
```

## 📁 Project Structure

```
nba-3point-predictor/
├── ml/                          # Machine Learning Pipeline
│   ├── scripts/
│   │   ├── config.py           # Configuration & constants
│   │   ├── data_processing.py  # Data cleaning & feature engineering
│   │   ├── preprocessing.py    # Train/test split & encoding
│   │   ├── models.py           # Model definitions & evaluation
│   │   ├── visualization.py    # Plots (confusion matrix, ROC, etc.)
│   │   ├── reporting.py        # Report generation
│   │   ├── pipeline_utils.py   # Model save/load utilities
│   │   └── utils.py            # Helper functions
│   ├── data/
│   │   ├── raw/                # Raw shot data CSVs
│   │   └── processed/          # Cleaned datasets
│   ├── models/                 # Saved model artifacts
│   │   ├── best_model.pkl      # XGBoost model
│   │   ├── encoders.pkl        # Categorical encoders
│   │   └── scaler.pkl          # Feature scaler
│   ├── outputs/                # Training outputs
│   │   ├── plots/              # Confusion matrix, ROC curve, etc.
│   │   ├── reports/            # Model report & data quality report
│   │   └── metrics/            # Model comparison metrics
│   ├── train.py                # Training CLI
│   ├── evaluate.py             # Evaluation CLI
│   ├── predict.py              # Prediction CLI
│   └── requirements.txt        # Python dependencies
├── backend/                    # FastAPI Backend
│   ├── app.py                  # FastAPI application
│   └── requirements.txt        # Backend dependencies
├── frontend/                   # React Frontend
│   └── index.html              # Single-page application
├── Dockerfile                  # Docker image for backend
├── docker-compose.yml          # Docker Compose orchestration
├── nginx.conf                  # Nginx configuration
└── README.md                   # This file
```

## 🔧 Configuration

Edit `ml/scripts/config.py` to customize:
- Input/output paths
- Feature columns
- Model hyperparameters
- Thresholds (late-game seconds, corner three zones, etc.)

## 📊 Model Performance

| Metric      | Value  |
|-------------|--------|
| Accuracy   | 98.9%  |
| Precision  | 98.1%  |
| Recall     | 100%   |
| F1 Score   | 99%    |
| ROC-AUC    | 99.3%  |

## 🔄 Training Pipeline

```bash
# Train on default dataset (ml/data/processed/synthesized_balanced_shots.csv)
cd ml
python train.py

# Train on custom dataset
python train.py --data path/to/dataset.csv

# Evaluate model
python evaluate.py

# Make single prediction
python predict.py \
  --shotDistance 25 \
  --shotZone "Above the Break 3" \
  --period 2 \
  --minutesRemaining 5 \
  --secondsRemaining 30 \
  --shotClock 10 \
  --defenderDistance 5 \
  --dribbles 2 \
  --touchTime 1.5 \
  --locationX 50 \
  --locationY 250
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -an | grep 8000

# Kill process using port 8000 (Linux/macOS)
lsof -ti:8000 | xargs kill -9
```

### Frontend can't connect to backend
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in `backend/app.py`
- Verify firewall rules allow port 8000

### Model not loading
- Ensure `ml/models/best_model.pkl` exists
- Check that all dependencies in `backend/requirements.txt` are installed
- Verify Python path includes the `ml` module

## 📝 Next Steps

- [ ] Add Streamlit dashboard for model monitoring
- [ ] Implement model retraining pipeline
- [ ] Add authentication and user management
- [ ] Deploy to AWS/GCP/Azure
- [ ] Add real-time player statistics from NBA API
- [ ] Implement A/B testing framework

## 📚 Technical Stack

- **ML**: scikit-learn, XGBoost, pandas, numpy
- **Backend**: FastAPI, uvicorn, pydantic
- **Frontend**: React, HTML5, CSS3
- **Deployment**: Docker, Docker Compose, nginx
- **Data**: NBA Stats API, CSV

## 📄 License

MIT License - feel free to use this project for learning and commercial purposes.

## 👤 Author

Built as an NBA 3-Point Prediction and Analysis System for Final Year Project.

---

**Questions or Issues?** Check the troubleshooting section or open an issue in the repository.
