# PowerShell Script to Create IAM Role for Lambda Function
# This script creates an IAM role with necessary permissions for the Drought Predictor Lambda

param(
    [string]$RoleName = "drought-predictor-lambda-role"
)

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

Write-Info "Creating IAM role for Lambda function..."

# Check if role already exists
$roleExists = aws iam get-role --role-name $RoleName 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Role '$RoleName' already exists"
    $roleArn = aws iam get-role --role-name $RoleName --query Role.Arn --output text
} else {
    # Create the role
    Write-Info "Creating IAM role: $RoleName"
    aws iam create-role `
        --role-name $RoleName `
        --assume-role-policy-document file://trust-policy.json `
        --description "Execution role for Drought Predictor Lambda function"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to create IAM role"
        exit 1
    }
    
    Write-Success "IAM role created"
    
    # Attach basic Lambda execution policy
    Write-Info "Attaching Lambda execution policy..."
    aws iam attach-role-policy `
        --role-name $RoleName `
        --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to attach execution policy"
        exit 1
    }
    
    Write-Success "Lambda execution policy attached"
    
    # Wait for role to be available
    Write-Info "Waiting for role to be available (10 seconds)..."
    Start-Sleep -Seconds 10
    
    $roleArn = aws iam get-role --role-name $RoleName --query Role.Arn --output text
}

Write-Info "`n========================================="
Write-Success "IAM Role Ready"
Write-Info "========================================="
Write-Info "Role Name: $RoleName"
Write-Info "Role ARN: $roleArn"
Write-Info "=========================================`n"
Write-Info "Use this ARN when deploying the Lambda function:"
Write-Success ".\deploy-lambda.ps1 -Role '$roleArn'"
Write-Info ""
