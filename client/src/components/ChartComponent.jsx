import { useState } from 'react';
import PropTypes from 'prop-types';
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
} from 'recharts';
import '../styles/ChartComponent.css';

// Helper function to format dates
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
};

// Custom tooltip component to show date and NDVI values
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length > 0) {
    const data = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="tooltip-date">{formatDate(data.date)}</p>
        {data.historical !== null && (
          <p className="tooltip-value" style={{ color: '#2563eb' }}>
            Historical NDVI: {data.historical.toFixed(3)}
          </p>
        )}
        {data.forecast !== null && (
          <>
            <p className="tooltip-value" style={{ color: '#f97316' }}>
              Forecast NDVI: {data.forecast.toFixed(3)}
            </p>
            {data.lower !== null && data.upper !== null && (
              <p className="tooltip-range" style={{ color: '#666', fontSize: '0.85em' }}>
                Range: {data.lower.toFixed(3)} - {data.upper.toFixed(3)}
              </p>
            )}
          </>
        )}
      </div>
    );
  }
  return null;
};

CustomTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
};

// Custom label component for drought event reference lines
const DroughtEventLabel = ({ viewBox, onMouseEnter, onMouseLeave }) => {
  const { x, y } = viewBox;
  
  return (
    <g>
      <circle
        cx={x}
        cy={y + 10}
        r={6}
        fill="#dc2626"
        stroke="#fff"
        strokeWidth={2}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        style={{ cursor: 'pointer' }}
      />
      <text
        x={x}
        y={y + 10}
        fill="#fff"
        fontSize={10}
        fontWeight="bold"
        textAnchor="middle"
        dominantBaseline="central"
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        style={{ cursor: 'pointer', pointerEvents: 'none' }}
      >
        !
      </text>
    </g>
  );
};

DroughtEventLabel.propTypes = {
  viewBox: PropTypes.object,
  onMouseEnter: PropTypes.func,
  onMouseLeave: PropTypes.func,
};

/**
 * ChartComponent - Renders interactive time series chart
 * Displays historical NDVI data, forecasts with confidence intervals,
 * and drought event markers
 */
function ChartComponent({ historicalData, forecastData, droughtEvents, loading }) {
  // State for drought event tooltip
  const [hoveredEvent, setHoveredEvent] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  
  // State for zoom/pan - track brush indices
  const [brushStartIndex, setBrushStartIndex] = useState(null);
  const [brushEndIndex, setBrushEndIndex] = useState(null);
  // Show skeleton loader when loading
  if (loading) {
    return (
      <div className="chart-component">
        <h2>NDVI Time Series</h2>
        <div className="chart-skeleton">
          <div className="skeleton-chart-area"></div>
        </div>
      </div>
    );
  }

  // Combine historical and forecast data for the chart
  const chartData = [
    ...historicalData.map((point) => ({
      date: point.date,
      historical: point.ndvi,
      forecast: null,
      lower: null,
      upper: null,
      type: 'historical',
    })),
    ...forecastData.map((point) => ({
      date: point.date,
      historical: null,
      forecast: point.ndvi,
      lower: point.lower,
      upper: point.upper,
      type: 'forecast',
    })),
  ];

  // Handle brush change for zoom/pan
  const handleBrushChange = (brushData) => {
    if (brushData && brushData.startIndex !== undefined && brushData.endIndex !== undefined) {
      setBrushStartIndex(brushData.startIndex);
      setBrushEndIndex(brushData.endIndex);
    }
  };

  // Reset zoom to default view
  const handleResetZoom = () => {
    setBrushStartIndex(null);
    setBrushEndIndex(null);
  };

  // Check if zoom is active
  const isZoomed = brushStartIndex !== null && brushEndIndex !== null;

  return (
    <div className="chart-component">
      <div className="chart-header">
        <h2>NDVI Time Series</h2>
        {isZoomed && (
          <button 
            className="reset-zoom-button" 
            onClick={handleResetZoom}
            title="Reset zoom to default view"
          >
            Reset Zoom
          </button>
        )}
      </div>
      {chartData.length === 0 ? (
        <p className="no-data">No data available to display</p>
      ) : (
        <ResponsiveContainer width="100%" height={500}>
          <LineChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            
            {/* X-axis with date formatting */}
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              angle={-45}
              textAnchor="end"
              height={80}
              stroke="#6b7280"
            />
            
            {/* Y-axis with NDVI values */}
            <YAxis
              label={{ value: 'NDVI', angle: -90, position: 'insideLeft' }}
              domain={[-0.1, 1]}
              stroke="#6b7280"
            />
            
            {/* Tooltip */}
            <Tooltip content={<CustomTooltip />} />
            
            {/* Legend */}
            <Legend
              verticalAlign="top"
              height={36}
              wrapperStyle={{ paddingBottom: '10px' }}
            />
            
            {/* Confidence interval area (shaded) */}
            <Area
              type="monotone"
              dataKey="upper"
              stroke="none"
              fill="#fed7aa"
              fillOpacity={0.3}
              name="Confidence Interval"
              connectNulls={false}
            />
            <Area
              type="monotone"
              dataKey="lower"
              stroke="none"
              fill="#ffffff"
              fillOpacity={1}
              connectNulls={false}
            />
            
            {/* Historical data line (blue) */}
            <Line
              type="monotone"
              dataKey="historical"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
              name="Historical NDVI"
              connectNulls={false}
            />
            
            {/* Forecast data line (orange) */}
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#f97316"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ fill: '#f97316', r: 4 }}
              name="Forecast NDVI"
              connectNulls={false}
            />
            
            {/* Drought event markers */}
            {droughtEvents.map((event, index) => {
              const handleMouseEnter = (e) => {
                setHoveredEvent(event);
                setTooltipPosition({ x: e.clientX, y: e.clientY });
              };
              
              const handleMouseLeave = () => {
                setHoveredEvent(null);
              };
              
              return (
                <ReferenceLine
                  key={`event-${index}`}
                  x={event.date}
                  stroke="#dc2626"
                  strokeWidth={2}
                  strokeDasharray="3 3"
                  label={
                    <DroughtEventLabel 
                      onMouseEnter={handleMouseEnter}
                      onMouseLeave={handleMouseLeave}
                    />
                  }
                  ifOverflow="extendDomain"
                />
              );
            })}
            
            {/* Brush component for zoom and pan */}
            <Brush
              dataKey="date"
              height={30}
              stroke="#2563eb"
              tickFormatter={formatDate}
              onChange={handleBrushChange}
              startIndex={brushStartIndex}
              endIndex={brushEndIndex}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
      
      {/* Drought event tooltip */}
      {hoveredEvent && (
        <div 
          className="drought-event-tooltip"
          style={{
            position: 'fixed',
            left: `${tooltipPosition.x + 10}px`,
            top: `${tooltipPosition.y + 10}px`,
            pointerEvents: 'none',
            zIndex: 1000,
          }}
        >
          <div className="drought-event-tooltip-content">
            <p className="drought-event-date">{formatDate(hoveredEvent.date)}</p>
            <p className="drought-event-description">{hoveredEvent.description}</p>
          </div>
        </div>
      )}
    </div>
  );
}

ChartComponent.propTypes = {
  historicalData: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string.isRequired,
      ndvi: PropTypes.number.isRequired,
    })
  ),
  forecastData: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string.isRequired,
      ndvi: PropTypes.number.isRequired,
      lower: PropTypes.number.isRequired,
      upper: PropTypes.number.isRequired,
    })
  ),
  droughtEvents: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
    })
  ),
  loading: PropTypes.bool,
};

ChartComponent.defaultProps = {
  historicalData: [],
  forecastData: [],
  droughtEvents: [],
  loading: false,
};

export default ChartComponent;
