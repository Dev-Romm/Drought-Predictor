import PropTypes from 'prop-types';
import '../styles/InsightPanel.css';

/**
 * InsightPanel - Displays pastoralist-friendly interpretation messages
 * Shows drought alert level and actionable insights
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
 */
function InsightPanel({ droughtAlert, insights }) {
  if (!droughtAlert) {
    return (
      <div className="insight-panel">
        <p className="no-insights">No insights available</p>
      </div>
    );
  }

  // Get icon based on drought level
  const getAlertIcon = (level) => {
    switch (level) {
      case 'Normal':
        return '✅';
      case 'Alert':
        return '⚠️';
      case 'Alarm':
        return '🔶';
      case 'Emergency':
        return '🚨';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className="insight-panel">
      <div
        className="alert-banner"
        style={{ backgroundColor: droughtAlert.colorCode || '#95a5a6' }}
      >
        <div className="alert-header">
          <span className="alert-icon" role="img" aria-label={`${droughtAlert.level} alert`}>
            {getAlertIcon(droughtAlert.level)}
          </span>
          <h2>Drought Alert: {droughtAlert.level}</h2>
        </div>
        <p className="alert-message">{droughtAlert.message}</p>
      </div>

      {insights && insights.length > 0 && (
        <div className="insights-list">
          <h3>Key Insights & Recommendations</h3>
          <ul>
            {insights.map((insight, index) => (
              <li key={index}>
                <span className="insight-text">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

InsightPanel.propTypes = {
  droughtAlert: PropTypes.shape({
    level: PropTypes.string,
    message: PropTypes.string,
    colorCode: PropTypes.string,
  }),
  insights: PropTypes.arrayOf(PropTypes.string),
};

InsightPanel.defaultProps = {
  droughtAlert: null,
  insights: [],
};

export default InsightPanel;
