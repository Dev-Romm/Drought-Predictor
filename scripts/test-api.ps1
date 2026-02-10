Write-Host "=== API Testing ===" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"
$passed = 0
$failed = 0

# Test 1: Health Check
Write-Host "`nTest 1: Health Check"
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/health" -UseBasicParsing
    if ($r.status -eq "healthy") {
        Write-Host "PASSED" -ForegroundColor Green
        $passed++
    }
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    $failed++
}

# Test 2: Historical Data
Write-Host "`nTest 2: Historical Data"
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/api/historical-data" -UseBasicParsing
    if ($r.Count -gt 0) {
        Write-Host "PASSED - $($r.Count) data points" -ForegroundColor Green
        $passed++
    }
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    $failed++
}

# Test 3: Drought Events
Write-Host "`nTest 3: Drought Events"
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/api/drought-events" -UseBasicParsing
    Write-Host "PASSED - $($r.Count) events" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    $failed++
}

# Test 4: Prophet Prediction
Write-Host "`nTest 4: Prophet Prediction (4 weeks)"
try {
    $body = @{model="prophet"; horizon=4} | ConvertTo-Json
    $r = Invoke-RestMethod -Uri "$baseUrl/api/predict" -Method Post -Body $body -ContentType "application/json" -UseBasicParsing
    if ($r.dates.Count -eq 2) {
        Write-Host "PASSED - Drought: $($r.drought_level)" -ForegroundColor Green
        $passed++
    }
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    $failed++
}

# Test 5: LSTM Prediction
Write-Host "`nTest 5: LSTM Prediction (4 weeks)"
try {
    $body = @{model="lstm"; horizon=4} | ConvertTo-Json
    $r = Invoke-RestMethod -Uri "$baseUrl/api/predict" -Method Post -Body $body -ContentType "application/json" -UseBasicParsing
    if ($r.dates.Count -eq 2) {
        Write-Host "PASSED - Drought: $($r.drought_level)" -ForegroundColor Green
        $passed++
    }
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    $failed++
}

# Test 6: 6-week horizon
Write-Host "`nTest 6: Prophet 6-week horizon"
try {
    $body = @{model="prophet"; horizon=6} | ConvertTo-Json
    $r = Invoke-RestMethod -Uri "$baseUrl/api/predict" -Method Post -Body $body -ContentType "application/json" -UseBasicParsing
    if ($r.dates.Count -eq 3) {
        Write-Host "PASSED - 3 data points" -ForegroundColor Green
        $passed++
    }
} catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    $failed++
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
