"""
Unit tests for Prophet model inference.
"""

import pytest
import pickle
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, mock_open
import sys
import os

# Add server directory to path (parent of tests directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prophet_inference import ProphetPredictor


class TestProphetPredictor:
    """Test suite for ProphetPredictor class."""
    
    def test_load_model_success(self):
        """Test successful model loading from pickle file."""
        # Create a mock Prophet model
        mock_model = Mock()
        
        # Mock the file opening and pickle loading
        with patch('builtins.open', mock_open(read_data=b'mock_data')):
            with patch('pickle.load', return_value=mock_model):
                predictor = ProphetPredictor('fake_model.pkl')
                assert predictor.model == mock_model
    
    def test_load_model_file_not_found(self):
        """Test error handling when model file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            ProphetPredictor('nonexistent_model.pkl')
    
    def test_predict_with_mock_model(self):
        """Test prediction with mock Prophet model."""
        # Create a mock Prophet model
        mock_model = Mock()
        
        # Create mock forecast data
        forecast_data = pd.DataFrame({
            'ds': [datetime(2026, 2, 1), datetime(2026, 2, 15)],
            'yhat': [0.38, 0.35],
            'yhat_lower': [0.32, 0.28],
            'yhat_upper': [0.44, 0.42]
        })
        mock_model.predict.return_value = forecast_data
        
        # Mock the model loading
        with patch('builtins.open', mock_open(read_data=b'mock_data')):
            with patch('pickle.load', return_value=mock_model):
                predictor = ProphetPredictor('fake_model.pkl')
        
        # Test prediction for 2 periods
        last_date = datetime(2026, 1, 18)
        result = predictor.predict(periods=2, last_date=last_date)
        
        # Verify the result structure
        assert 'dates' in result
        assert 'ndvi' in result
        assert 'lower' in result
        assert 'upper' in result
        
        # Verify the result values
        assert len(result['dates']) == 2
        assert len(result['ndvi']) == 2
        assert len(result['lower']) == 2
        assert len(result['upper']) == 2
        
        # Verify date format (ISO 8601)
        assert result['dates'][0] == '2026-02-01'
        assert result['dates'][1] == '2026-02-15'
        
        # Verify NDVI values
        assert result['ndvi'][0] == 0.38
        assert result['ndvi'][1] == 0.35
        
        # Verify confidence bounds
        assert result['lower'][0] == 0.32
        assert result['upper'][0] == 0.44
    
    def test_predict_single_period(self):
        """Test prediction for 1 period (2 weeks)."""
        mock_model = Mock()
        
        forecast_data = pd.DataFrame({
            'ds': [datetime(2026, 2, 1)],
            'yhat': [0.40],
            'yhat_lower': [0.35],
            'yhat_upper': [0.45]
        })
        mock_model.predict.return_value = forecast_data
        
        with patch('builtins.open', mock_open(read_data=b'mock_data')):
            with patch('pickle.load', return_value=mock_model):
                predictor = ProphetPredictor('fake_model.pkl')
        
        last_date = datetime(2026, 1, 18)
        result = predictor.predict(periods=1, last_date=last_date)
        
        assert len(result['dates']) == 1
        assert len(result['ndvi']) == 1
        assert len(result['lower']) == 1
        assert len(result['upper']) == 1
    
    def test_predict_three_periods(self):
        """Test prediction for 3 periods (6 weeks)."""
        mock_model = Mock()
        
        forecast_data = pd.DataFrame({
            'ds': [
                datetime(2026, 2, 1),
                datetime(2026, 2, 15),
                datetime(2026, 3, 1)
            ],
            'yhat': [0.38, 0.35, 0.32],
            'yhat_lower': [0.32, 0.28, 0.25],
            'yhat_upper': [0.44, 0.42, 0.39]
        })
        mock_model.predict.return_value = forecast_data
        
        with patch('builtins.open', mock_open(read_data=b'mock_data')):
            with patch('pickle.load', return_value=mock_model):
                predictor = ProphetPredictor('fake_model.pkl')
        
        last_date = datetime(2026, 1, 18)
        result = predictor.predict(periods=3, last_date=last_date)
        
        assert len(result['dates']) == 3
        assert len(result['ndvi']) == 3
        assert len(result['lower']) == 3
        assert len(result['upper']) == 3
    
    def test_predict_generates_correct_future_dates(self):
        """Test that future dates are generated with correct biweekly intervals."""
        mock_model = Mock()
        
        # Capture the future dataframe passed to predict
        captured_future = None
        def capture_predict(future_df):
            nonlocal captured_future
            captured_future = future_df
            return pd.DataFrame({
                'ds': future_df['ds'],
                'yhat': [0.4] * len(future_df),
                'yhat_lower': [0.3] * len(future_df),
                'yhat_upper': [0.5] * len(future_df)
            })
        
        mock_model.predict.side_effect = capture_predict
        
        with patch('builtins.open', mock_open(read_data=b'mock_data')):
            with patch('pickle.load', return_value=mock_model):
                predictor = ProphetPredictor('fake_model.pkl')
        
        last_date = datetime(2026, 1, 1)
        predictor.predict(periods=2, last_date=last_date)
        
        # Verify that future dates are 14 days apart
        assert captured_future is not None
        dates = captured_future['ds'].tolist()
        assert len(dates) == 2
        assert dates[0] == datetime(2026, 1, 15)  # 14 days after Jan 1
        assert dates[1] == datetime(2026, 1, 29)  # 28 days after Jan 1
