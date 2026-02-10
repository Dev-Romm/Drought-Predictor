# Scripts

This directory contains utility scripts for testing and development.

## Available Scripts

### test-api.ps1

**Purpose:** Automated API endpoint testing

**Description:** PowerShell script that runs automated tests against the backend API to verify all endpoints are working correctly.

**Usage:**
```powershell
# From the scripts directory
.\test-api.ps1

# From the project root
.\scripts\test-api.ps1

# Or with full path
powershell -ExecutionPolicy Bypass -File scripts/test-api.ps1
```

**Prerequisites:**
- Backend server must be running on http://localhost:8000
- PowerShell 5.0 or higher

**Tests Performed:**
1. Health Check - Verifies server is running
2. Historical Data - Tests `/api/historical-data` endpoint
3. Drought Events - Tests `/api/drought-events` endpoint
4. Prophet Prediction (4 weeks) - Tests Prophet model
5. LSTM Prediction (4 weeks) - Tests LSTM model
6. Prophet Prediction (6 weeks) - Tests horizon conversion

**Output:**
- Displays PASSED/FAILED for each test
- Shows summary with total passed/failed count
- Exit code 0 if all tests pass, 1 if any fail

**When to Use:**
- After making backend changes
- Before deployment
- During development for quick verification
- As part of CI/CD pipeline

## Adding New Scripts

When adding new scripts to this directory:
1. Use descriptive names (e.g., `deploy-backend.ps1`, `seed-data.py`)
2. Add documentation to this README
3. Include usage examples
4. Document prerequisites and dependencies
