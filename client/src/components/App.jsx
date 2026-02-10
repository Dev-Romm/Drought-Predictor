import { useState, useEffect, useCallback } from 'react';
import {
  fetchHistoricalData as apiFetchHistoricalData,
  fetchPrediction as apiFetchPrediction,
  fetchDroughtEvents as apiFetchDroughtEvents,
} from '../services/api';
import ChartComponent from './ChartComponent';
import MetricsDisplay from './MetricsDisplay';
import ControlPanel from './ControlPanel';
import InsightPanel from './InsightPanel';
import '../styles/App.css';

/**
 * Main application component for Drought Predictor
 * Manages application state and coordinates child components
 */
function App() {
  // State management
  const [historicalData, setHistoricalData] = useState([]);
  const [forecastData, setForecastData] = useState([]);
  const [forecastHorizon, setForecastHorizon] = useState(4);
  const [droughtAlert, setDroughtAlert] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [droughtEvents, setDroughtEvents] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Fetch historical NDVI data from the backend
   */
  const fetchHistoricalDataHandler = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiFetchHistoricalData();
      
      // Filter data to show only from 2019 onwards
      const filteredData = data.filter(point => {
        const year = new Date(point.date).getFullYear();
        return year >= 2019;
      });
      
      setHistoricalData(filteredData);
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch historical data. Please try again.';
      setError({
        message: errorMessage,
        type: 'historical',
        retry: fetchHistoricalDataHandler,
      });
      console.error('Failed to fetch historical data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch prediction from the backend
   * @param {number} horizon - Forecast horizon in weeks (2, 4, or 6)
   */
  const fetchPredictionHandler = useCallback(async (horizon) => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiFetchPrediction(horizon);

      // Transform response data to match component expectations
      const forecast = response.dates.map((date, index) => ({
        date,
        ndvi: response.ndvi[index],
        lower: response.lower[index],
        upper: response.upper[index],
      }));

      setForecastData(forecast);

      // Set drought alert
      setDroughtAlert({
        level: response.drought_level,
        message: response.insights?.[0] || 'No message available',
        colorCode: response.color_code,
      });

      // Set insights
      setInsights(response.insights || []);

      // Calculate and set metrics
      if (historicalData.length > 0 && forecast.length > 0) {
        const currentNDVI = historicalData[historicalData.length - 1].ndvi;
        const currentDate = historicalData[historicalData.length - 1].date;
        const predictedNDVI = forecast[forecast.length - 1].ndvi;
        const predictedDate = forecast[forecast.length - 1].date;
        const changePercent = response.change_rate;

        setMetrics({
          currentNDVI,
          currentDate,
          predictedNDVI,
          predictedDate,
          changePercent,
        });
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to generate prediction. Please try again.';
      setError({
        message: errorMessage,
        type: 'prediction',
        retry: () => fetchPredictionHandler(horizon),
      });
      console.error('Failed to fetch prediction:', err);
    } finally {
      setLoading(false);
    }
  }, [historicalData]);

  /**
   * Fetch historical drought events from the backend
   */
  const fetchDroughtEventsHandler = useCallback(async () => {
    try {
      setError(null);
      const events = await apiFetchDroughtEvents();
      setDroughtEvents(events);
    } catch (err) {
      // Don't set error for drought events as they're optional
      // Just log the error
      console.error('Failed to fetch drought events:', err);
    }
  }, []);

  /**
   * Handle retry for failed requests
   */
  const handleRetry = () => {
    if (error && error.retry) {
      error.retry();
    }
  };

  // Load initial data on mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        setError(null);
        await fetchHistoricalDataHandler();
        await fetchDroughtEventsHandler();
      } catch (err) {
        // Errors are already handled in individual fetch functions
        console.error('Error loading initial data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, [fetchHistoricalDataHandler, fetchDroughtEventsHandler]);

  // Fetch prediction when horizon changes
  useEffect(() => {
    if (historicalData.length > 0) {
      fetchPredictionHandler(forecastHorizon);
    }
  }, [forecastHorizon, historicalData.length, fetchPredictionHandler]);

  /**
   * Handle forecast horizon change
   * @param {number} horizon - Selected forecast horizon in weeks
   */
  const handleHorizonChange = (horizon) => {
    setForecastHorizon(horizon);
  };

  /**
   * Handle manual prediction trigger
   */
  const handlePredict = () => {
    if (historicalData.length > 0) {
      fetchPredictionHandler(forecastHorizon);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Drought Predictor - Turkana County</h1>
      </header>

      {error && (
        <div className="error-banner">
          <div className="error-content">
            <strong>Error:</strong> {typeof error === 'string' ? error : error.message}
          </div>
          <div className="error-actions">
            {error.retry && (
              <button onClick={handleRetry} className="retry-button">
                Retry
              </button>
            )}
            <button onClick={() => setError(null)} className="dismiss-button">
              Dismiss
            </button>
          </div>
        </div>
      )}

      <main>
        <section className="welcome-section">
          <div className="welcome-content">
            <h2>Welcome to Drought Predictor</h2>
            <p className="intro-text">
              Monitor and forecast vegetation health in Turkana County, Kenya using satellite-based NDVI data 
              and advanced time series forecasting.
            </p>
            
            <div className="info-cards">
              <div className="info-card">
                <div className="info-icon">📊</div>
                <h3>Historical Data</h3>
                <p>View NDVI trends from 2019 onwards to understand past vegetation patterns</p>
              </div>
              
              <div className="info-card">
                <div className="info-icon">🔮</div>
                <h3>Forecast</h3>
                <p>Generate predictions for 2, 4, or 6 weeks ahead using Prophet forecasting</p>
              </div>
              
              <div className="info-card">
                <div className="info-icon">⚠️</div>
                <h3>Drought Alerts</h3>
                <p>Get early warnings about potential drought conditions with actionable insights</p>
              </div>
            </div>
            
            <div className="how-to-use">
              <h3>How to Use</h3>
              <ol>
                <li><strong>Select Forecast Horizon:</strong> Choose how far ahead you want to predict (2, 4, or 6 weeks)</li>
                <li><strong>Generate Prediction:</strong> Click the "Predict" button to generate a forecast</li>
                <li><strong>Review Results:</strong> Examine the chart, metrics, and insights for drought risk assessment</li>
              </ol>
            </div>
          </div>
        </section>

        <ControlPanel
          forecastHorizon={forecastHorizon}
          onHorizonChange={handleHorizonChange}
          onPredict={handlePredict}
          loading={loading}
        />

        {loading && historicalData.length === 0 ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading data...</p>
          </div>
        ) : (
          <>
            {loading && (
              <div className="loading-overlay">
                <div className="spinner"></div>
                <p>Generating prediction...</p>
              </div>
            )}

            <MetricsDisplay metrics={metrics} droughtAlert={droughtAlert} loading={loading && !metrics} />

            <ChartComponent
              historicalData={historicalData}
              forecastData={forecastData}
              droughtEvents={droughtEvents}
              loading={loading && historicalData.length === 0}
            />

            <InsightPanel droughtAlert={droughtAlert} insights={insights} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
