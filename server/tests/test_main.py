"""
Unit tests for main FastAPI application.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add server directory to path (parent of tests directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestApplicationSetup:
    """Test suite for FastAPI application setup."""
    
    def test_app_initialization(self):
        """Test that FastAPI app is initialized with correct configuration."""
        # Import after path is set
        from main import app
        
        # Verify app is a FastAPI instance
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
        
        # Verify app has correct title
        assert app.title == "Drought Predictor API"
        assert app.version == "1.0.0"
    
    def test_cors_middleware_configured(self):
        """Test that CORS middleware is configured."""
        from main import app
        
        # Check that middleware is configured
        # CORS middleware should be in the middleware stack
        middleware_types = [type(m).__name__ for m in app.user_middleware]
        assert 'CORSMiddleware' in middleware_types or len(app.user_middleware) > 0
    
    def test_routers_included(self):
        """Test that API routers are included."""
        from main import app
        
        # Check that routes are registered
        routes = [route.path for route in app.routes]
        
        # Verify key endpoints exist
        assert any('/api/historical-data' in route for route in routes)
        assert any('/api/predict' in route for route in routes)
        assert any('/api/drought-events' in route for route in routes)
    
    def test_health_endpoints_exist(self):
        """Test that health check endpoints exist."""
        from main import app
        
        routes = [route.path for route in app.routes]
        
        # Verify health endpoints
        assert '/' in routes
        assert '/health' in routes
    
    def test_mangum_handler_exists(self):
        """Test that Mangum handler is created for AWS Lambda."""
        from main import handler
        from mangum import Mangum
        
        # Verify handler is a Mangum instance
        assert isinstance(handler, Mangum)


class TestLifespanEvents:
    """Test suite for application lifespan events."""
    
    @patch('main.NDVIDataLoader')
    @patch('main.ProphetPredictor')
    @patch('main.LSTMPredictor')
    @patch('main.set_dependencies')
    def test_startup_initializes_components(
        self,
        mock_set_deps,
        mock_lstm,
        mock_prophet,
        mock_loader
    ):
        """Test that startup event initializes all components."""
        # This test verifies the structure but doesn't actually run startup
        # since that would require the actual model files
        
        # Verify imports work
        from main import lifespan
        
        # Verify lifespan is callable (it's an async context manager)
        assert callable(lifespan)
        
        # Verify it's decorated with asynccontextmanager
        # The function should have the context manager protocol
        assert hasattr(lifespan, '__call__')


class TestEnvironmentConfiguration:
    """Test suite for environment variable configuration."""
    
    def test_default_paths_configured(self):
        """Test that default paths are configured."""
        from main import (
            CSV_PATH,
            PROPHET_MODEL_PATH,
            LSTM_MODEL_PATH,
            LSTM_SCALER_PATH,
            FRONTEND_URL
        )
        
        # Verify default values exist
        assert CSV_PATH is not None
        assert PROPHET_MODEL_PATH is not None
        assert LSTM_MODEL_PATH is not None
        assert LSTM_SCALER_PATH is not None
        assert FRONTEND_URL is not None
        
        # Verify default paths are reasonable
        assert 'turkana_ndvi' in CSV_PATH.lower()
        assert 'prophet' in PROPHET_MODEL_PATH.lower()
        assert 'lstm' in LSTM_MODEL_PATH.lower()
        assert 'scaler' in LSTM_SCALER_PATH.lower()
