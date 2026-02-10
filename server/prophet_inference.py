"""
Prophet model inference module for NDVI forecasting.

This module provides functionality to load a pre-trained Prophet model
and generate NDVI forecasts with confidence intervals.
"""

import pickle
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from prophet import Prophet


class ProphetPredictor:
    """
    Prophet-based NDVI forecasting predictor.
    
    Loads a pre-trained Prophet model and generates forecasts for specified
    time periods with native confidence intervals.
    """
    
    def __init__(self, model_path: str):
        """
        Initialize the Prophet predictor.
        
        Args:
            model_path: Path to the pickled Prophet model file
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        self.model = self.load_model(model_path)
    
    def load_model(self, path: str) -> Prophet:
        """
        Load a Prophet model from a pickle file.
        
        Args:
            path: Path to the pickled model file
            
        Returns:
            Loaded Prophet model instance
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If unpickling fails
        """
        try:
            with open(path, 'rb') as f:
                model = pickle.load(f)
            return model
        except FileNotFoundError:
            raise FileNotFoundError(f"Prophet model file not found: {path}")
        except Exception as e:
            raise Exception(f"Failed to load Prophet model: {str(e)}")
    
    def predict(self, periods: int, last_date: datetime = None) -> Dict[str, List]:
        """
        Generate NDVI forecasts for specified number of biweekly periods.
        
        Args:
            periods: Number of biweekly prediction steps (1, 2, or 3)
            last_date: Last date in historical data (optional, defaults to today)
            
        Returns:
            Dictionary containing:
                - dates: List of forecast dates in ISO 8601 format
                - ndvi: List of predicted NDVI values (yhat)
                - lower: List of lower confidence bounds (yhat_lower)
                - upper: List of upper confidence bounds (yhat_upper)
                
        Example:
            {
                "dates": ["2026-02-01", "2026-02-15"],
                "ndvi": [0.38, 0.35],
                "lower": [0.32, 0.28],
                "upper": [0.44, 0.42]
            }
        """
        # Use current date if last_date not provided
        if last_date is None:
            last_date = datetime.now()
        
        # Generate future dataframe for specified periods
        # Prophet expects biweekly (14-day) intervals
        future_dates = []
        for i in range(1, periods + 1):
            future_date = last_date + timedelta(days=14 * i)
            future_dates.append(future_date)
        
        # Create future dataframe with 'ds' column (Prophet's expected format)
        future = pd.DataFrame({'ds': future_dates})
        
        # Generate predictions
        forecast = self.model.predict(future)
        
        # Extract yhat, yhat_lower, yhat_upper from predictions
        dates = [date.strftime('%Y-%m-%d') for date in forecast['ds']]
        ndvi_values = forecast['yhat'].tolist()
        lower_bounds = forecast['yhat_lower'].tolist()
        upper_bounds = forecast['yhat_upper'].tolist()
        
        # Return forecast with dates, NDVI values, and confidence intervals
        return {
            'dates': dates,
            'ndvi': ndvi_values,
            'lower': lower_bounds,
            'upper': upper_bounds
        }
