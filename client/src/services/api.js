import axios from 'axios';

// Get API base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

/**
 * Fetch historical NDVI data from the backend
 * @returns {Promise<Array>} Array of {date, ndvi} objects
 * @throws {Error} Network or server error
 */
export async function fetchHistoricalData() {
  try {
    const response = await apiClient.get('/api/historical-data');
    return response.data;
  } catch (error) {
    console.error('Error fetching historical data:', error);
    
    if (error.response) {
      // Server responded with error status
      throw new Error(
        `Failed to fetch historical data: ${error.response.data?.error?.message || error.response.statusText}`
      );
    } else if (error.request) {
      // Request made but no response received
      throw new Error('Unable to connect to the server. Please check your connection and try again.');
    } else {
      // Error in request setup
      throw new Error(`Request error: ${error.message}`);
    }
  }
}

/**
 * Fetch prediction from the backend
 * @param {number} horizon - Forecast horizon in weeks (2, 4, or 6)
 * @returns {Promise<Object>} Prediction response with forecast data, drought alert, and insights
 * @throws {Error} Network, validation, or server error
 */
export async function fetchPrediction(horizon) {
  try {
    // Validate parameters
    if (![2, 4, 6].includes(horizon)) {
      throw new Error(`Invalid forecast horizon: ${horizon}. Must be 2, 4, or 6 weeks.`);
    }

    const response = await apiClient.post('/api/predict', {
      horizon,
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching prediction:', error);
    
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const errorMessage = error.response.data?.error?.message || error.response.statusText;
      
      if (status === 400) {
        throw new Error(`Invalid request: ${errorMessage}`);
      } else if (status === 500) {
        throw new Error(`Server error: ${errorMessage}`);
      } else {
        throw new Error(`Failed to fetch prediction: ${errorMessage}`);
      }
    } else if (error.request) {
      // Request made but no response received
      throw new Error('Unable to connect to the server. Please check your connection and try again.');
    } else {
      // Error in request setup or validation
      throw new Error(error.message || 'Request error occurred');
    }
  }
}

/**
 * Fetch historical drought events from the backend
 * @returns {Promise<Array>} Array of {date, description} objects
 * @throws {Error} Network or server error
 */
export async function fetchDroughtEvents() {
  try {
    const response = await apiClient.get('/api/drought-events');
    return response.data;
  } catch (error) {
    console.error('Error fetching drought events:', error);
    
    if (error.response) {
      // Server responded with error status
      throw new Error(
        `Failed to fetch drought events: ${error.response.data?.error?.message || error.response.statusText}`
      );
    } else if (error.request) {
      // Request made but no response received
      throw new Error('Unable to connect to the server. Please check your connection and try again.');
    } else {
      // Error in request setup
      throw new Error(`Request error: ${error.message}`);
    }
  }
}

export default {
  fetchHistoricalData,
  fetchPrediction,
  fetchDroughtEvents,
};
