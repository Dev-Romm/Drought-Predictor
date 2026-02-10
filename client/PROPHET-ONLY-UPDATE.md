# Client Update: Prophet-Only Forecasting

## Date: February 9, 2026

## Summary

Updated the Drought Predictor client to remove LSTM model selection and use only Prophet for forecasting, matching the backend changes.

## Changes Made

### 1. ControlPanel Component (`src/components/ControlPanel.jsx`)
**Removed:**
- Model selection dropdown
- `selectedModel` prop
- `onModelChange` prop

**Added:**
- Model info display showing "Using Prophet forecasting model"
- Simplified component to only handle horizon selection

**Before:**
```jsx
<ControlPanel
  selectedModel={selectedModel}
  forecastHorizon={forecastHorizon}
  onModelChange={handleModelChange}
  onHorizonChange={handleHorizonChange}
  onPredict={handlePredict}
  loading={loading}
/>
```

**After:**
```jsx
<ControlPanel
  forecastHorizon={forecastHorizon}
  onHorizonChange={handleHorizonChange}
  onPredict={handlePredict}
  loading={loading}
/>
```

### 2. API Service (`src/services/api.js`)
**Updated `fetchPrediction` function:**
- Removed `model` parameter
- Only sends `horizon` to backend
- Removed model validation logic

**Before:**
```javascript
export async function fetchPrediction(model, horizon) {
  // Validate model and horizon
  const response = await apiClient.post('/api/predict', {
    model,
    horizon,
  });
  return response.data;
}
```

**After:**
```javascript
export async function fetchPrediction(horizon) {
  // Validate horizon only
  const response = await apiClient.post('/api/predict', {
    horizon,
  });
  return response.data;
}
```

### 3. App Component (`src/components/App.jsx`)
**Removed:**
- `selectedModel` state
- `handleModelChange` function
- Model parameter from `fetchPredictionHandler`
- Model dependency from useEffect

**Updated:**
- `fetchPredictionHandler` now only takes `horizon` parameter
- useEffect only depends on `forecastHorizon` (not `selectedModel`)
- Simplified prediction trigger logic

### 4. Styling (`src/styles/ControlPanel.css`)
**Added:**
- `.model-info` class for displaying model information
- Styled info box with left border and background color
- Responsive styling for model info text

## User Experience Changes

### Before
Users could select between two models:
- Prophet (statistical forecasting)
- LSTM (deep learning)

### After
- Single forecasting model (Prophet) used automatically
- Clear indication that Prophet is being used
- Simplified interface with fewer options
- Faster, more reliable predictions

## Benefits

1. **Simplified UX**: Fewer choices for users, clearer interface
2. **Consistency**: Client matches backend capabilities
3. **Reliability**: No confusion about which model to use
4. **Performance**: Faster predictions with Prophet-only backend
5. **Maintenance**: Easier to maintain single-model system

## Testing Checklist

- [x] Control panel displays correctly without model selector
- [x] Horizon selection works properly
- [x] Predict button triggers forecasts
- [x] Model info displays "Using Prophet forecasting model"
- [x] API calls send only horizon parameter
- [x] Predictions display correctly
- [x] No console errors
- [x] Responsive design works on mobile

## Deployment Notes

No environment variable changes needed. The client will automatically work with the updated backend API that expects only `horizon` parameter.

## Rollback Plan

If needed to rollback:
1. Restore previous versions of:
   - `src/components/ControlPanel.jsx`
   - `src/services/api.js`
   - `src/components/App.jsx`
   - `src/styles/ControlPanel.css`
2. Ensure backend supports both `model` and `horizon` parameters
