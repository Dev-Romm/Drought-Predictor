"""
API routes for the Drought Predictor backend.

This module defines FastAPI endpoints for historical data retrieval,
drought prediction, and drought event information.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np

from data_loader import NDVIDataLoader
from prophet_inference import ProphetPredictor
from drought_classifier import DroughtClassifier, DroughtLevel
from insight_generator import InsightGenerator


# Pydantic models for request/response validation

class PredictionRequest(BaseModel):
    """Request model for prediction endpoint."""
    horizon: int = Field(..., description="Forecast horizon in weeks: 2, 4, 6, 8, 10, or 12")
    
    @field_validator('horizon')
    @classmethod
    def validate_horizon(cls, v: int) -> int:
        """Validate forecast horizon."""
        if v not in [2, 4, 6, 8, 10, 12]:
            raise ValueError("Horizon must be 2, 4, 6, 8, 10, or 12 weeks")
        return v


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""
    dates: List[str] = Field(..., description="Forecast dates in ISO 8601 format")
    ndvi: List[float] = Field(..., description="Predicted NDVI values")
    lower: List[float] = Field(..., description="Lower confidence bounds")
    upper: List[float] = Field(..., description="Upper confidence bounds")
    drought_level: str = Field(..., description="Classified drought severity level")
    change_rate: float = Field(..., description="Percentage change in NDVI")
    insights: List[str] = Field(..., description="Pastoralist-friendly insight messages")
    color_code: str = Field(..., description="Hex color code for drought level")


class HistoricalDataPoint(BaseModel):
    """Model for a single historical data point."""
    date: str = Field(..., description="Date in ISO 8601 format")
    ndvi: float = Field(..., description="NDVI value")


class DroughtEvent(BaseModel):
    """Model for a historical drought event."""
    date: str = Field(..., description="Event date in ISO 8601 format")
    description: str = Field(..., description="Event description")


# Initialize routers
data_router = APIRouter(prefix="/api", tags=["data"])
prediction_router = APIRouter(prefix="/api", tags=["prediction"])


# Global variables for model instances (initialized in main.py)
data_loader: Optional[NDVIDataLoader] = None
prophet_predictor: Optional[ProphetPredictor] = None
drought_classifier: Optional[DroughtClassifier] = None
insight_generator: Optional[InsightGenerator] = None


def set_dependencies(
    loader: NDVIDataLoader,
    prophet: ProphetPredictor,
    classifier: DroughtClassifier,
    generator: InsightGenerator
) -> None:
    """
    Set global dependencies for route handlers.
    
    Args:
        loader: Initialized NDVIDataLoader instance
        prophet: Initialized ProphetPredictor instance
        classifier: Initialized DroughtClassifier instance
        generator: Initialized InsightGenerator instance
    """
    global data_loader, prophet_predictor, drought_classifier, insight_generator
    data_loader = loader
    prophet_predictor = prophet
    drought_classifier = classifier
    insight_generator = generator


@data_router.get(
    "/historical-data",
    response_model=List[HistoricalDataPoint],
    status_code=status.HTTP_200_OK,
    summary="Get historical NDVI data",
    description="Returns historical NDVI time series data from 2017 to January 2026"
)
async def get_historical_data() -> List[Dict[str, any]]:
    """
    Get historical NDVI data.
    
    Returns:
        List of historical data points with date and NDVI values
        
    Raises:
        HTTPException: 500 if data loading fails
        
    Requirements: 8.1
    """
    try:
        if data_loader is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data loader not initialized"
            )
        
        historical_data = data_loader.get_historical_data()
        return historical_data
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve historical data: {str(e)}"
        )


@data_router.get(
    "/drought-events",
    response_model=List[DroughtEvent],
    status_code=status.HTTP_200_OK,
    summary="Get historical drought events",
    description="Returns a list of historical drought events for chart overlay"
)
async def get_drought_events() -> List[Dict[str, str]]:
    """
    Get historical drought events for chart markers.
    
    Returns:
        List of drought events with date and description
        
    Requirements: 8.4
    """
    try:
        # Hardcoded historical drought events for Turkana County
        # These can be moved to a database or configuration file in the future
        events = [
            {
                "date": "2019-06-15",
                "description": "Severe drought - Emergency declared"
            },
            {
                "date": "2022-03-01",
                "description": "Moderate drought - Alert issued"
            },
            {
                "date": "2023-08-15",
                "description": "Drought conditions - Alarm level"
            }
        ]
        return events
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve drought events: {str(e)}"
        )


@prediction_router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate NDVI forecast",
    description="Generates NDVI forecast using Prophet model"
)
async def predict(request: PredictionRequest) -> Dict[str, any]:
    """
    Generate NDVI forecast with drought classification and insights.
    
    Args:
        request: PredictionRequest with forecast horizon
        
    Returns:
        PredictionResponse with forecast data, drought alert, and insights
        
    Raises:
        HTTPException: 400 for invalid parameters, 500 for server errors
        
    Requirements: 8.2, 8.3, 8.6
    """
    try:
        # Validate dependencies are initialized
        if any(dep is None for dep in [
            data_loader, prophet_predictor,
            drought_classifier, insight_generator
        ]):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server dependencies not initialized"
            )
        
        # Convert horizon weeks to biweekly periods (Requirements 3.3, 3.4, 3.5)
        periods = request.horizon // 2
        
        # Get current NDVI value
        current_ndvi = data_loader.get_latest_ndvi()
        
        # Get last date from historical data
        historical_df = data_loader.get_data_for_model()
        last_date = historical_df.iloc[-1]['date']
        
        # Generate forecast using Prophet model (Requirement 2.3)
        forecast = prophet_predictor.predict(periods=periods, last_date=last_date)
        
        # Get predicted NDVI at forecast endpoint
        predicted_ndvi = forecast['ndvi'][-1]
        
        # Classify drought severity (Requirement 5.1)
        drought_level, change_rate = drought_classifier.classify(
            current_ndvi=current_ndvi,
            predicted_ndvi=predicted_ndvi
        )
        
        # Get color code for drought level (Requirement 5.7)
        color_code = drought_classifier.get_color_code(drought_level)
        
        # Generate pastoralist-friendly insights (Requirement 6.1-6.6)
        insights = insight_generator.generate_insights(
            level=drought_level,
            change_rate=change_rate,
            predicted_ndvi=predicted_ndvi,
            horizon_weeks=request.horizon
        )
        
        # Return prediction response (Requirement 8.3)
        return {
            'dates': forecast['dates'],
            'ndvi': forecast['ndvi'],
            'lower': forecast['lower'],
            'upper': forecast['upper'],
            'drought_level': drought_level.value,
            'change_rate': change_rate,
            'insights': insights,
            'color_code': color_code
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except ValueError as e:
        # Handle validation errors (Requirement 8.6)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request parameters: {str(e)}"
        )
    
    except Exception as e:
        # Handle unexpected errors (Requirement 8.6)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )
