"""
Main FastAPI application for the Drought Predictor backend.

This module initializes the FastAPI application, configures CORS middleware,
loads models and data on startup, and provides AWS Lambda compatibility.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
from contextlib import asynccontextmanager

from data_loader import NDVIDataLoader
from prophet_inference import ProphetPredictor
from drought_classifier import DroughtClassifier
from insight_generator import InsightGenerator
from routes import data_router, prediction_router, set_dependencies


# Configuration from environment variables
CSV_PATH = os.getenv("CSV_PATH", "turkana_ndvi_csv_biweekly.csv")
PROPHET_MODEL_PATH = os.getenv("PROPHET_MODEL_PATH", "models/ndvi_prophet_model.pkl")
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    
    Initializes data loader, predictors, classifier, and insight generator
    on startup (Requirements 9.1, 9.2, 9.3).
    
    Args:
        app: FastAPI application instance
    """
    # Startup: Initialize all components
    print("Initializing Drought Predictor backend...")
    
    try:
        # Initialize data loader (Requirement 1.4)
        print(f"Loading NDVI data from {CSV_PATH}...")
        data_loader = NDVIDataLoader(csv_path=CSV_PATH)
        print(f"Loaded {len(data_loader.data)} historical data points")
        
        # Initialize Prophet predictor (Requirement 9.1)
        print(f"Loading Prophet model from {PROPHET_MODEL_PATH}...")
        prophet_predictor = ProphetPredictor(model_path=PROPHET_MODEL_PATH)
        print("Prophet model loaded successfully")
        
        # Initialize drought classifier
        print("Initializing drought classifier...")
        drought_classifier = DroughtClassifier()
        print("Drought classifier initialized")
        
        # Initialize insight generator
        print("Initializing insight generator...")
        insight_generator = InsightGenerator()
        print("Insight generator initialized")
        
        # Set dependencies for route handlers
        set_dependencies(
            loader=data_loader,
            prophet=prophet_predictor,
            classifier=drought_classifier,
            generator=insight_generator
        )
        
        print("All components initialized successfully!")
        print("Drought Predictor backend is ready to serve requests")
        
    except Exception as e:
        print(f"ERROR: Failed to initialize backend: {str(e)}")
        raise
    
    # Yield control to the application
    yield
    
    # Shutdown: Cleanup (if needed)
    print("Shutting down Drought Predictor backend...")


# Initialize FastAPI application (Requirement 8.5)
app = FastAPI(
    title="Drought Predictor API",
    description="NDVI-based drought forecasting API for Turkana County, Kenya",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS middleware (Requirement 8.5, 11.2)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers (Requirement 8.5)
app.include_router(data_router)
app.include_router(prediction_router)


# Root endpoint for health check
@app.get("/", tags=["health"])
async def root():
    """
    Root endpoint for health check.
    
    Returns:
        Simple status message indicating the API is running
    """
    return {
        "message": "Drought Predictor API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Health status of the API
    """
    return {
        "status": "healthy",
        "service": "drought-predictor-api"
    }


# AWS Lambda handler using Mangum (Requirement 11.2)
handler = Mangum(app)
