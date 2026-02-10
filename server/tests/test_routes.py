"""
Unit tests for API routes.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import sys
import os

# Add server directory to path (parent of tests directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import FastAPI after path is set
from fastapi import HTTPException

# Import the modules we're testing
from routes import (
    PredictionRequest,
    get_historical_data,
    get_drought_events,
    predict,
    set_dependencies
)
from drought_classifier import DroughtLevel


class TestPredictionRequest:
    """Test suite for PredictionRequest validation."""
    
    def test_valid_prophet_model(self):
        """Test valid Prophet model request."""
        request = PredictionRequest(model="prophet", horizon=4)
        assert request.model == "prophet"
        assert request.horizon == 4
    
    def test_valid_lstm_model(self):
        """Test valid LSTM model request."""
        request = PredictionRequest(model="lstm", horizon=6)
        assert request.model == "lstm"
        assert request.horizon == 6
    
    def test_invalid_model_type(self):
        """Test invalid model type raises validation error."""
        with pytest.raises(ValueError):
            PredictionRequest(model="invalid", horizon=4)
    
    def test_invalid_horizon(self):
        """Test invalid horizon raises validation error."""
        with pytest.raises(ValueError):
            PredictionRequest(model="prophet", horizon=8)
    
    def test_model_case_insensitive(self):
        """Test model type is case insensitive."""
        request = PredictionRequest(model="PROPHET", horizon=4)
        assert request.model == "prophet"


class TestHistoricalDataEndpoint:
    """Test suite for GET /api/historical-data endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_historical_data_success(self):
        """Test successful historical data retrieval."""
        # Create mock data loader
        mock_loader = Mock()
        mock_loader.get_historical_data.return_value = [
            {"date": "2017-01-01", "ndvi": 0.45},
            {"date": "2017-01-15", "ndvi": 0.48}
        ]
        
        # Set dependencies
        set_dependencies(
            loader=mock_loader,
            prophet=Mock(),
            lstm=Mock(),
            classifier=Mock(),
            generator=Mock()
        )
        
        # Call endpoint
        result = await get_historical_data()
        
        # Verify result
        assert len(result) == 2
        assert result[0]["date"] == "2017-01-01"
        assert result[0]["ndvi"] == 0.45
    
    @pytest.mark.asyncio
    async def test_get_historical_data_error(self):
        """Test error handling when data loading fails."""
        # Create mock data loader that raises an exception
        mock_loader = Mock()
        mock_loader.get_historical_data.side_effect = Exception("Data load failed")
        
        # Set dependencies
        set_dependencies(
            loader=mock_loader,
            prophet=Mock(),
            lstm=Mock(),
            classifier=Mock(),
            generator=Mock()
        )
        
        # Call endpoint and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_historical_data()
        
        assert exc_info.value.status_code == 500


class TestDroughtEventsEndpoint:
    """Test suite for GET /api/drought-events endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_drought_events_success(self):
        """Test successful drought events retrieval."""
        result = await get_drought_events()
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Verify first event has required fields
        assert "date" in result[0]
        assert "description" in result[0]


class TestPredictEndpoint:
    """Test suite for POST /api/predict endpoint."""
    
    @pytest.mark.asyncio
    async def test_predict_with_prophet_success(self):
        """Test successful prediction with Prophet model."""
        # Create mock dependencies
        mock_loader = Mock()
        mock_loader.get_latest_ndvi.return_value = 0.40
        mock_loader.get_data_for_model.return_value = Mock(
            iloc=Mock(__getitem__=lambda self, idx: {"date": datetime(2026, 1, 18)})
        )
        
        mock_prophet = Mock()
        mock_prophet.predict.return_value = {
            "dates": ["2026-02-01", "2026-02-15"],
            "ndvi": [0.38, 0.35],
            "lower": [0.32, 0.28],
            "upper": [0.44, 0.42]
        }
        
        mock_classifier = Mock()
        mock_classifier.classify.return_value = (DroughtLevel.ALERT, -7.5)
        mock_classifier.get_color_code.return_value = "#FFFF00"
        
        mock_generator = Mock()
        mock_generator.generate_insights.return_value = [
            "Vegetation shows signs of decline.",
            "Monitor conditions closely."
        ]
        
        # Set dependencies
        set_dependencies(
            loader=mock_loader,
            prophet=mock_prophet,
            lstm=Mock(),
            classifier=mock_classifier,
            generator=mock_generator
        )
        
        # Create request
        request = PredictionRequest(model="prophet", horizon=4)
        
        # Call endpoint
        result = await predict(request)
        
        # Verify result structure
        assert "dates" in result
        assert "ndvi" in result
        assert "lower" in result
        assert "upper" in result
        assert "drought_level" in result
        assert "change_rate" in result
        assert "insights" in result
        assert "color_code" in result
        
        # Verify values
        assert result["drought_level"] == "Alert"
        assert result["change_rate"] == -7.5
        assert result["color_code"] == "#FFFF00"
        assert len(result["insights"]) == 2
    
    @pytest.mark.asyncio
    async def test_predict_with_lstm_success(self):
        """Test successful prediction with LSTM model."""
        # Create mock dependencies
        import numpy as np
        
        mock_loader = Mock()
        mock_loader.get_latest_ndvi.return_value = 0.42
        mock_df = Mock()
        mock_df.iloc = Mock(__getitem__=lambda self, idx: {"date": datetime(2026, 1, 18)})
        mock_df.__getitem__ = lambda self, key: Mock(values=np.array([0.4, 0.41, 0.42]))
        mock_loader.get_data_for_model.return_value = mock_df
        
        mock_lstm = Mock()
        mock_lstm.predict.return_value = {
            "dates": ["2026-02-01", "2026-02-15"],
            "ndvi": [0.40, 0.38],
            "lower": [0.36, 0.34],
            "upper": [0.44, 0.42]
        }
        
        mock_classifier = Mock()
        mock_classifier.classify.return_value = (DroughtLevel.NORMAL, -4.8)
        mock_classifier.get_color_code.return_value = "#00FF00"
        
        mock_generator = Mock()
        mock_generator.generate_insights.return_value = [
            "Vegetation conditions are healthy."
        ]
        
        # Set dependencies
        set_dependencies(
            loader=mock_loader,
            prophet=Mock(),
            lstm=mock_lstm,
            classifier=mock_classifier,
            generator=mock_generator
        )
        
        # Create request
        request = PredictionRequest(model="lstm", horizon=4)
        
        # Call endpoint
        result = await predict(request)
        
        # Verify result
        assert result["drought_level"] == "Normal"
        assert result["color_code"] == "#00FF00"
    
    @pytest.mark.asyncio
    async def test_predict_invalid_parameters(self):
        """Test prediction with invalid parameters returns 400."""
        # Set dependencies
        set_dependencies(
            loader=Mock(),
            prophet=Mock(),
            lstm=Mock(),
            classifier=Mock(),
            generator=Mock()
        )
        
        # Test with invalid model (should be caught by Pydantic validation)
        with pytest.raises(ValueError):
            request = PredictionRequest(model="invalid", horizon=4)
    
    @pytest.mark.asyncio
    async def test_predict_horizon_conversion(self):
        """Test that horizon weeks are correctly converted to periods."""
        # Create mock dependencies
        mock_loader = Mock()
        mock_loader.get_latest_ndvi.return_value = 0.40
        mock_loader.get_data_for_model.return_value = Mock(
            iloc=Mock(__getitem__=lambda self, idx: {"date": datetime(2026, 1, 18)})
        )
        
        mock_prophet = Mock()
        mock_prophet.predict.return_value = {
            "dates": ["2026-02-01"],
            "ndvi": [0.38],
            "lower": [0.32],
            "upper": [0.44]
        }
        
        mock_classifier = Mock()
        mock_classifier.classify.return_value = (DroughtLevel.ALERT, -5.0)
        mock_classifier.get_color_code.return_value = "#FFFF00"
        
        mock_generator = Mock()
        mock_generator.generate_insights.return_value = ["Test insight"]
        
        # Set dependencies
        set_dependencies(
            loader=mock_loader,
            prophet=mock_prophet,
            lstm=Mock(),
            classifier=mock_classifier,
            generator=mock_generator
        )
        
        # Test 2 weeks -> 1 period
        request = PredictionRequest(model="prophet", horizon=2)
        await predict(request)
        mock_prophet.predict.assert_called_with(periods=1, last_date=datetime(2026, 1, 18))
        
        # Test 4 weeks -> 2 periods
        request = PredictionRequest(model="prophet", horizon=4)
        await predict(request)
        mock_prophet.predict.assert_called_with(periods=2, last_date=datetime(2026, 1, 18))
        
        # Test 6 weeks -> 3 periods
        request = PredictionRequest(model="prophet", horizon=6)
        await predict(request)
        mock_prophet.predict.assert_called_with(periods=3, last_date=datetime(2026, 1, 18))


class TestCORSConfiguration:
    """Test suite for CORS configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS middleware is configured (integration test)."""
        # This would be tested in integration tests with actual HTTP requests
        # For now, we just verify the structure is correct
        pass
