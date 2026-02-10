import PropTypes from 'prop-types';
import '../styles/MetricsDisplay.css';

/**
 * Format date for display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
};

/**
 * MetricsDisplay - Shows key metrics in card format
 * Displays current NDVI, predicted NDVI, change percentage, and drought stage
 */
function MetricsDisplay({ metrics, droughtAlert, loading }) {
  if (loading) {
    return (
      <div className="metrics-display">
        <h2>Key Metrics</h2>
        <div className="metrics-grid">
          <div className="metric-card skeleton">
            <div className="skeleton-text"></div>
            <div className="skeleton-value"></div>
          </div>
          <div className="metric-card skeleton">
            <div className="skeleton-text"></div>
            <div className="skeleton-value"></div>
          </div>
          <div className="metric-card skeleton">
            <div className="skeleton-text"></div>
            <div className="skeleton-value"></div>
          </div>
          <div className="metric-card skeleton">
            <div className="skeleton-text"></div>
            <div className="skeleton-value"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return <div className="metrics-display">No metrics available yet. Generate a prediction to see metrics.</div>;
  }

  return (
    <div className="metrics-display">
      <h2>Key Metrics</h2>
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Latest NDVI</h3>
          <p className="metric-value">{metrics.currentNDVI?.toFixed(3) || 'N/A'}</p>
          {metrics.currentDate && (
            <p className="metric-date">{formatDate(metrics.currentDate)}</p>
          )}
        </div>
        <div className="metric-card">
          <h3>Predicted NDVI</h3>
          <p className="metric-value">{metrics.predictedNDVI?.toFixed(3) || 'N/A'}</p>
          {metrics.predictedDate && (
            <p className="metric-date">{formatDate(metrics.predictedDate)}</p>
          )}
        </div>
        <div className="metric-card">
          <h3>NDVI Change %</h3>
          <p className="metric-value">
            {metrics.changePercent !== null && metrics.changePercent !== undefined
              ? `${metrics.changePercent > 0 ? '+' : ''}${metrics.changePercent.toFixed(1)}%`
              : 'N/A'}
          </p>
        </div>
        <div className="metric-card">
          <h3>Drought Stage</h3>
          <div 
            className="drought-badge"
            style={{ 
              backgroundColor: droughtAlert?.colorCode || '#e9ecef',
              color: '#fff'
            }}
          >
            {droughtAlert?.level || 'N/A'}
          </div>
        </div>
      </div>
    </div>
  );
}

MetricsDisplay.propTypes = {
  metrics: PropTypes.shape({
    currentNDVI: PropTypes.number,
    currentDate: PropTypes.string,
    predictedNDVI: PropTypes.number,
    predictedDate: PropTypes.string,
    changePercent: PropTypes.number,
  }),
  droughtAlert: PropTypes.shape({
    level: PropTypes.string,
    message: PropTypes.string,
    colorCode: PropTypes.string,
  }),
  loading: PropTypes.bool,
};

MetricsDisplay.defaultProps = {
  metrics: null,
  droughtAlert: null,
  loading: false,
};

export default MetricsDisplay;
