# PowerShell Deployment Script for Drought Predictor Backend to AWS Lambda
# This script builds a Docker image and deploys it to AWS Lambda

param(
    [string]$Region = "us-east-1",
    [string]$FunctionName = "drought-predictor-api",
    [string]$Role = "",
    [int]$Memory = 2048,
    [int]$Timeout = 60,
    [string]$ImageTag = "latest"
)

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

# Check if AWS credentials are configured
Write-Info "Checking AWS credentials..."
$awsIdentity = aws sts get-caller-identity 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
}
Write-Success "AWS credentials verified"

# Get AWS account ID
$accountId = (aws sts get-caller-identity --query Account --output text)
Write-Info "AWS Account ID: $accountId"

# Set ECR repository name
$ecrRepo = "drought-predictor"
$ecrUri = "$accountId.dkr.ecr.$Region.amazonaws.com/$ecrRepo"

Write-Host ""
Write-Info "========================================="
Write-Info "Drought Predictor Lambda Deployment"
Write-Info "========================================="
Write-Info "Region: $Region"
Write-Info "Function Name: $FunctionName"
Write-Info "ECR Repository: $ecrRepo"
Write-Info "Memory: $Memory MB"
Write-Info "Timeout: $Timeout seconds"
Write-Info "========================================="
Write-Host ""

# Step 1: Create ECR repository if it doesn't exist
Write-Info "Step 1: Checking ECR repository..."
$repoExists = aws ecr describe-repositories --repository-names $ecrRepo --region $Region 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Info "Creating ECR repository: $ecrRepo"
    aws ecr create-repository --repository-name $ecrRepo --region $Region | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to create ECR repository"
        exit 1
    }
    Write-Success "ECR repository created successfully"
} else {
    Write-Success "ECR repository already exists"
}

# Step 2: Authenticate Docker to ECR
Write-Host ""
Write-Info "Step 2: Authenticating Docker to ECR..."
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$Region.amazonaws.com" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Failed to authenticate Docker to ECR"
    exit 1
}
Write-Success "Docker authenticated to ECR"

# Step 3: Build Docker image
Write-Host ""
Write-Info "Step 3: Building Docker image..."
Write-Info "This may take several minutes..."
docker build -t "${ecrRepo}:${ImageTag}" -f Dockerfile .
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Failed to build Docker image"
    exit 1
}
Write-Success "Docker image built successfully"

# Step 4: Tag image for ECR
Write-Host ""
Write-Info "Step 4: Tagging Docker image for ECR..."
docker tag "${ecrRepo}:${ImageTag}" "${ecrUri}:${ImageTag}"
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Failed to tag Docker image"
    exit 1
}
Write-Success "Docker image tagged"

# Step 5: Push image to ECR
Write-Host ""
Write-Info "Step 5: Pushing Docker image to ECR..."
Write-Info "This may take several minutes..."
docker push "${ecrUri}:${ImageTag}"
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Failed to push Docker image to ECR"
    exit 1
}
Write-Success "Docker image pushed to ECR"

# Step 6: Create or update Lambda function
Write-Host ""
Write-Info "Step 6: Deploying Lambda function..."

# Check if Lambda function exists
$functionExists = aws lambda get-function --function-name $FunctionName --region $Region 2>&1
if ($LASTEXITCODE -eq 0) {
    # Update existing function
    Write-Info "Updating existing Lambda function..."
    aws lambda update-function-code --function-name $FunctionName --image-uri "${ecrUri}:${ImageTag}" --region $Region | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to update Lambda function code"
        exit 1
    }
    
    # Wait for update to complete
    Write-Info "Waiting for function update to complete..."
    aws lambda wait function-updated --function-name $FunctionName --region $Region
    
    # Update function configuration
    Write-Info "Updating function configuration..."
    aws lambda update-function-configuration --function-name $FunctionName --memory-size $Memory --timeout $Timeout --region $Region | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to update Lambda function configuration"
        exit 1
    }
    
    Write-Success "Lambda function updated successfully"
} else {
    # Create new function
    if ([string]::IsNullOrEmpty($Role)) {
        Write-ErrorMsg "Lambda execution role ARN is required for new function creation."
        Write-Info "Please provide the role ARN using -Role parameter"
        Write-Info "Example: -Role 'arn:aws:iam::123456789012:role/lambda-execution-role'"
        exit 1
    }
    
    Write-Info "Creating new Lambda function..."
    aws lambda create-function --function-name $FunctionName --package-type Image --code "ImageUri=${ecrUri}:${ImageTag}" --role $Role --memory-size $Memory --timeout $Timeout --region $Region | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to create Lambda function"
        exit 1
    }
    
    Write-Success "Lambda function created successfully"
}

# Step 7: Create Function URL (for HTTP access)
Write-Host ""
Write-Info "Step 7: Configuring Function URL..."
$functionUrlConfig = aws lambda get-function-url-config --function-name $FunctionName --region $Region 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Info "Creating Function URL..."
    aws lambda create-function-url-config --function-name $FunctionName --auth-type NONE --cors "AllowOrigins=*,AllowMethods=*,AllowHeaders=*,MaxAge=86400" --region $Region | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to create Function URL"
    } else {
        Write-Success "Function URL created"
    }
    
    # Add permission for public access
    aws lambda add-permission --function-name $FunctionName --statement-id FunctionURLAllowPublicAccess --action lambda:InvokeFunctionUrl --principal "*" --function-url-auth-type NONE --region $Region 2>&1 | Out-Null
} else {
    Write-Success "Function URL already exists"
}

# Get Function URL
$functionUrl = aws lambda get-function-url-config --function-name $FunctionName --region $Region --query FunctionUrl --output text

# Step 8: Display deployment summary
Write-Host ""
Write-Info "========================================="
Write-Info "Deployment Summary"
Write-Info "========================================="
Write-Success "Docker image built and pushed to ECR"
Write-Success "Lambda function deployed"
Write-Success "Function URL configured"
Write-Host ""
Write-Info "Function Details:"
Write-Info "  Name: $FunctionName"
Write-Info "  Region: $Region"
Write-Info "  Memory: $Memory MB"
Write-Info "  Timeout: $Timeout seconds"
Write-Info "  Image: ${ecrUri}:${ImageTag}"
Write-Host ""
Write-Info "API Endpoint:"
Write-Success "  $functionUrl"
Write-Host ""
Write-Info "Test the API:"
Write-Info "  curl $functionUrl"
Write-Info "  curl ${functionUrl}api/historical-data"
Write-Info "========================================="
Write-Host ""

Write-Success "Deployment completed successfully!"
