import PropTypes from 'prop-types';
import '../styles/ControlPanel.css';

/**
 * ControlPanel - Provides user controls for horizon selection
 * Allows users to select forecast horizon
 */
function ControlPanel({
  forecastHorizon,
  onHorizonChange,
  onPredict,
  loading,
}) {
  const handlePredictClick = () => {
    if (onPredict) {
      onPredict();
    }
  };

  return (
    <div className="control-panel">
      <h2>Prediction Controls</h2>

      <div className="control-group">
        <label htmlFor="horizon-select">Forecast Horizon:</label>
        <select
          id="horizon-select"
          value={forecastHorizon}
          onChange={(e) => onHorizonChange(Number(e.target.value))}
          disabled={loading}
        >
          <option value={2}>2 weeks</option>
          <option value={4}>4 weeks</option>
          <option value={6}>6 weeks</option>
        </select>
      </div>

      <button
        className="predict-button"
        disabled={loading}
        onClick={handlePredictClick}
      >
        {loading ? 'Predicting...' : 'Predict'}
      </button>
      
      <div className="model-info">
        <small>Using Prophet forecasting model</small>
      </div>
    </div>
  );
}

ControlPanel.propTypes = {
  forecastHorizon: PropTypes.number.isRequired,
  onHorizonChange: PropTypes.func.isRequired,
  onPredict: PropTypes.func,
  loading: PropTypes.bool,
};

ControlPanel.defaultProps = {
  onPredict: null,
  loading: false,
};

export default ControlPanel;
