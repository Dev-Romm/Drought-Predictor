"""
Unit tests for LSTM inference module.
Tests model loading, prediction, scaling, and confidence interval calculation.
"""

import pytest
import numpy as np
import pickle
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
import sys
import os

# Add server directory to path (parent of tests directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lstm_inference import LSTMPredictor


class TestLSTMPredictor:
    """Test suite for LSTMPredictor class."""
    
    def test_init_loads_model_and_scaler(self):
        """Test that initialization loads both model and scaler."""
        with patch('lstm_inference.keras.models.load_model') as mock_load_model, \
             patch('lstm_inference.pickle.load') as mock_pickle_load:
            
            mock_model = Mock()
            mock_scaler = Mock()
            mock_load_model.return_value = mock_model
            mock_pickle_load.return_value = mock_scaler
            
            with patch('builtins.open', mock_open()):
                predictor = LSTMPredictor('model.keras', 'scaler.pkl', sequence_length=12)
            
            assert predictor.model is not None
            assert predictor.scaler is not None
            assert predictor.sequence_length == 12
    
    def test_load_model_file_not_found(self):
        """Test that FileNotFoundError is raised when model file doesn't exist."""
        with patch('lstm_inference.keras.models.load_model', side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError, match="LSTM model file not found"):
                predictor = LSTMPredictor('nonexistent.keras', 'scaler.pkl')
    
    def test_load_scaler_file_not_found(self):
        """Test that FileNotFoundError is raised when scaler file doesn't exist."""
        with patch('lstm_inference.keras.models.load_model', return_value=Mock()):
            with patch('builtins.open', side_effect=FileNotFoundError()):
                with pytest.raises(FileNotFoundError, match="Scaler file not found"):
                    predictor = LSTMPredictor('model.keras', 'nonexistent.pkl')
    
    def test_predict_with_valid_data(self):
        """Test prediction with valid historical data."""
        # Create mock model and scaler
        mock_model = Mock()
        mock_scaler = Mock()
        
        # Mock scaler transform/inverse_transform
        mock_scaler.transform.return_value = np.array([[0.5], [0.6], [0.7], [0.8], 
                                                        [0.9], [0.85], [0.8], [0.75],
                                                        [0.7], [0.65], [0.6], [0.55]])
        mock_scaler.inverse_transform.return_value = np.array([[0.35], [0.33]])
        
        # Mock model predictions
        mock_model.predict.side_effect = [
            np.array([[0.52]]),  # First prediction
            np.array([[0.50]])   # Second prediction
        ]
        
        with patch('lstm_inference.keras.models.load_model', return_value=mock_model), \
             patch('lstm_inference.pickle.load', return_value=mock_scaler), \
             patch('builtins.open', mock_open()):
            
            predictor = LSTMPredictor('model.keras', 'scaler.pkl', sequence_length=12)
            
            # Create historical data (12 points minimum)
            historical_data = np.array([0.4, 0.42, 0.45, 0.48, 0.5, 0.48, 0.46, 0.44, 0.42, 0.40, 0.38, 0.36])
            
            # Generate 2-period forecast
            result = predictor.predict(historical_data, periods=2, last_date=datetime(2026, 1, 15))
            
            # Verify result structure
            assert 'dates' in result
            assert 'ndvi' in result
            assert 'lower' in result
            assert 'upper' in result
            
            # Verify correct number of predictions
            assert len(result['dates']) == 2
            assert len(result['ndvi']) == 2
            assert len(result['lower']) == 2
            assert len(result['upper']) == 2
            
            # Verify dates are in ISO 8601 format
            assert result['dates'][0] == '2026-01-29'
            assert result['dates'][1] == '2026-02-12'
            
            # Verify confidence intervals
            for i in range(2):
                assert result['lower'][i] < result['ndvi'][i]
                assert result['upper'][i] > result['ndvi'][i]
    
    def test_predict_insufficient_data(self):
        """Test that ValueError is raised with insufficient historical data."""
        mock_model = Mock()
        mock_scaler = Mock()
        
        with patch('lstm_inference.keras.models.load_model', return_value=mock_model), \
             patch('lstm_inference.pickle.load', return_value=mock_scaler), \
             patch('builtins.open', mock_open()):
            
            predictor = LSTMPredictor('model.keras', 'scaler.pkl', sequence_length=12)
            
            # Only 5 data points (need 12)
            historical_data = np.array([0.4, 0.42, 0.45, 0.48, 0.5])
            
            with pytest.raises(ValueError, match="Insufficient historical data"):
                predictor.predict(historical_data, periods=2)
    
    def test_predict_autoregressive_forecasting(self):
        """Test that predictions use autoregressive approach."""
        mock_model = Mock()
        mock_scaler = Mock()
        
        # Mock scaler to return scaled values
        def mock_transform(data):
            return data * 2  # Simple scaling
        
        def mock_inverse_transform(data):
            return data / 2  # Simple inverse scaling
        
        mock_scaler.transform.side_effect = mock_transform
        mock_scaler.inverse_transform.side_effect = mock_inverse_transform
        
        # Mock model to return predictable values
        mock_model.predict.side_effect = [
            np.array([[0.8]]),  # First prediction
            np.array([[0.75]]), # Second prediction
            np.array([[0.7]])   # Third prediction
        ]
        
        with patch('lstm_inference.keras.models.load_model', return_value=mock_model), \
             patch('lstm_inference.pickle.load', return_value=mock_scaler), \
             patch('builtins.open', mock_open()):
            
            predictor = LSTMPredictor('model.keras', 'scaler.pkl', sequence_length=12)
            
            historical_data = np.array([0.4, 0.42, 0.45, 0.48, 0.5, 0.48, 0.46, 0.44, 0.42, 0.40, 0.38, 0.36])
            
            result = predictor.predict(historical_data, periods=3)
            
            # Verify model.predict was called 3 times (once per period)
            assert mock_model.predict.call_count == 3
            
            # Verify we got 3 predictions
            assert len(result['ndvi']) == 3
    
    def test_confidence_intervals_within_valid_range(self):
        """Test that confidence intervals are clipped to valid NDVI range [-1, 1]."""
        mock_model = Mock()
        mock_scaler = Mock()
        
        # Mock to return values that would exceed bounds
        mock_scaler.transform.return_value = np.array([[0.5]] * 12)
        mock_scaler.inverse_transform.return_value = np.array([[0.95]])  # High value
        mock_model.predict.return_value = np.array([[0.9]])
        
        with patch('lstm_inference.keras.models.load_model', return_value=mock_model), \
             patch('lstm_inference.pickle.load', return_value=mock_scaler), \
             patch('builtins.open', mock_open()):
            
            predictor = LSTMPredictor('model.keras', 'scaler.pkl', sequence_length=12)
            
            historical_data = np.array([0.4] * 12)
            result = predictor.predict(historical_data, periods=1)
            
            # Verify bounds are within [-1, 1]
            assert -1 <= result['lower'][0] <= 1
            assert -1 <= result['upper'][0] <= 1
    
    def test_predict_with_different_periods(self):
        """Test prediction for 1, 2, and 3 periods."""
        mock_model = Mock()
        mock_scaler = Mock()
        
        mock_scaler.transform.return_value = np.array([[0.5]] * 12)
        mock_scaler.inverse_transform.side_effect = [
            np.array([[0.35]]),
            np.array([[0.35], [0.33]]),
            np.array([[0.35], [0.33], [0.31]])
        ]
        
        mock_model.predict.return_value = np.array([[0.5]])
        
        with patch('lstm_inference.keras.models.load_model', return_value=mock_model), \
             patch('lstm_inference.pickle.load', return_value=mock_scaler), \
             patch('builtins.open', mock_open()):
            
            predictor = LSTMPredictor('model.keras', 'scaler.pkl', sequence_length=12)
            
            historical_data = np.array([0.4] * 12)
            
            # Test 1 period
            result1 = predictor.predict(historical_data, periods=1)
            assert len(result1['ndvi']) == 1
            
            # Test 2 periods
            result2 = predictor.predict(historical_data, periods=2)
            assert len(result2['ndvi']) == 2
            
            # Test 3 periods
            result3 = predictor.predict(historical_data, periods=3)
            assert len(result3['ndvi']) == 3
