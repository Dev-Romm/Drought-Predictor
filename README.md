# Drought Predictor

A web application that provides NDVI-based drought forecasting for Turkana County, Kenya. The system helps pastoralists make informed decisions about livestock management and migration planning by visualizing historical vegetation conditions and predicting future drought events.

## Overview

The Drought Predictor consists of:
- **React Frontend**: Interactive dashboard with data visualization, forecasts, and drought alerts
- **FastAPI Backend**: REST API server with ML model inference (Prophet and LSTM)
- **ML Models**: Pre-trained Prophet and LSTM models for NDVI forecasting

## Features

- Historical NDVI data visualization (2017-2026)
- Dual forecasting models (Prophet and LSTM)
- Configurable forecast horizons (2, 4, or 6 weeks)
- Drought severity classification (Normal, Alert, Alarm, Emergency)
- Pastoralist-friendly insights and recommendations
- Interactive charts with confidence intervals
- Real-time drought event markers

## Technology Stack

**Frontend:**
- React 18+
- Recharts for data visualization
- Axios for API requests

**Backend:**
- FastAPI
- Prophet (fbprophet) for time series forecasting
- TensorFlow/Keras for LSTM inference
- Pandas for data processing
- Mangum for AWS Lambda compatibility

## Prerequisites

**Frontend:**
- Node.js 16+ and npm

**Backend:**
- Python 3.10+
- pip

## Setup Instructions

### Backend Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

6. Edit `.env` to configure your environment variables

7. Ensure model files are present in `server/models/`:
   - `ndvi_prophet_model.pkl`
   - `ndvi_lstm_model.keras`
   - `ndvi_lstm_scaler.pkl`

8. Ensure the CSV data file exists at the root: `turkana_ndvi_csv_biweekly.csv`

### Frontend Setup

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Edit `.env` to set the backend API URL:
```
REACT_APP_API_URL=http://localhost:8000
```

## Running Locally

### Start the Backend

1. Navigate to the server directory and activate the virtual environment
2. Run the FastAPI server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Start the Frontend

1. Navigate to the client directory
2. Run the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

## Testing

### Backend Tests

Run unit tests and property-based tests:
```bash
cd server
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Frontend Tests

Run tests:
```bash
cd client
npm test
```

Run with coverage:
```bash
npm test -- --coverage
```

## Deployment

### Frontend Deployment (Vercel)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Navigate to the client directory:
```bash
cd client
```

3. Deploy to Vercel:
```bash
vercel
```

4. Set environment variables in Vercel dashboard:
   - `REACT_APP_API_URL`: Your deployed backend URL

### Backend Deployment (AWS Lambda)

1. Build the Docker image:
```bash
cd server
docker build -t drought-predictor-api .
```

2. Tag and push to Amazon ECR:
```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag drought-predictor-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/drought-predictor-api:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/drought-predictor-api:latest
```

3. Create Lambda function from container image in AWS Console

4. Configure Lambda:
   - Memory: 2048 MB (for ML models)
   - Timeout: 30 seconds
   - Environment variables: Set `FRONTEND_URL` to your Vercel URL

5. Create API Gateway to expose Lambda function

6. Update frontend `.env` with the API Gateway URL

## Project Structure

```
drought-predictor/
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API service layer
│   │   └── App.jsx           # Main application component
│   ├── .env.example
│   ├── .gitignore
│   └── package.json
├── server/                    # FastAPI backend
│   ├── models/               # Pre-trained ML models
│   │   ├── ndvi_prophet_model.pkl
│   │   ├── ndvi_lstm_model.keras
│   │   └── ndvi_lstm_scaler.pkl
│   ├── data_loader.py        # CSV data parsing
│   ├── prophet_inference.py  # Prophet model inference
│   ├── lstm_inference.py     # LSTM model inference
│   ├── drought_classifier.py # Drought severity classification
│   ├── insight_generator.py  # Insight message generation
│   ├── routes.py             # API endpoints
│   ├── main.py               # FastAPI application
│   ├── Dockerfile            # Container configuration
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example
│   └── .gitignore
├── turkana_ndvi_csv_biweekly.csv  # Historical NDVI data
└── README.md
```

## API Endpoints

### GET /api/historical-data
Returns historical NDVI data from 2017 to January 2026.

**Response:**
```json
[
  {
    "date": "2017-01-01",
    "ndvi": 0.452
  }
]
```

### POST /api/predict
Generates NDVI forecasts using the selected model.

**Request:**
```json
{
  "model": "prophet",
  "horizon": 4
}
```

**Response:**
```json
{
  "dates": ["2026-02-01", "2026-02-15"],
  "ndvi": [0.38, 0.35],
  "lower": [0.32, 0.28],
  "upper": [0.44, 0.42],
  "drought_level": "Alert",
  "change_rate": -7.2,
  "insights": [
    "Vegetation shows signs of decline (-7.2% over 4 weeks).",
    "Monitor conditions closely and prepare contingency plans."
  ],
  "color_code": "#FFA500"
}
```

### GET /api/drought-events
Returns historical drought events for chart overlay.

**Response:**
```json
[
  {
    "date": "2019-06-15",
    "description": "Severe drought - Emergency declared"
  }
]
```

## Contributing

1. Follow the existing code structure and style
2. Write tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting changes

## License

This project is intended for educational and humanitarian purposes to support pastoralist communities in Turkana County, Kenya.

## Support

For questions or issues, please refer to the project documentation in `.kiro/specs/drought-predictor/`.
