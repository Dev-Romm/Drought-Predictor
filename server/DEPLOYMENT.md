# Backend Deployment Guide

## Quick Deployment

For routine code updates, use the PowerShell deployment script:

```powershell
cd server
.\deploy-lambda.ps1
```

This script will:
1. ✅ Build the Docker image
2. ✅ Push to Amazon ECR
3. ✅ Update the Lambda function
4. ✅ Verify deployment

**Deployment time**: ~3-5 minutes

---

## Prerequisites

Before running the deployment script, ensure you have:

- **AWS CLI** installed and configured (`aws configure`)
- **Docker** installed and running
- **AWS credentials** with permissions for:
  - ECR (push images)
  - Lambda (update function)

---

## Current Configuration

### Lambda Function
- **Name**: `drought-predictor-api`
- **Region**: `us-east-1`
- **Memory**: 3008 MB
- **Timeout**: 120 seconds
- **Runtime**: Python 3.10 (Container)

### API Gateway
- **Type**: HTTP API (v2)
- **URL**: `https://ipkofutqtb.execute-api.us-east-1.amazonaws.com`
- **Note**: API Gateway is already configured and doesn't need updates for code changes

### ECR Repository
- **Name**: `drought-predictor`
- **URI**: `463040245883.dkr.ecr.us-east-1.amazonaws.com/drought-predictor`

---

## Deployment Scenarios

### 1. Code Update (Most Common)

When you've made changes to Python code, models, or dependencies:

```powershell
cd server
.\deploy-lambda.ps1
```

### 2. Custom Image Tag

To deploy with a specific version tag:

```powershell
.\deploy-lambda.ps1 -ImageTag "v1.2.0"
```

### 3. Change Memory or Timeout

```powershell
.\deploy-lambda.ps1 -Memory 4096 -Timeout 180
```

### 4. Manual Deployment (Step-by-Step)

If you prefer manual control:

```powershell
# 1. Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 463040245883.dkr.ecr.us-east-1.amazonaws.com

# 2. Build Docker image
docker build -t drought-predictor:latest .

# 3. Tag for ECR
docker tag drought-predictor:latest 463040245883.dkr.ecr.us-east-1.amazonaws.com/drought-predictor:latest

# 4. Push to ECR
docker push 463040245883.dkr.ecr.us-east-1.amazonaws.com/drought-predictor:latest

# 5. Update Lambda function
aws lambda update-function-code --function-name drought-predictor-api --image-uri 463040245883.dkr.ecr.us-east-1.amazonaws.com/drought-predictor:latest --region us-east-1

# 6. Wait for update to complete (15-30 seconds)
Start-Sleep -Seconds 20

# 7. Test the API
Invoke-RestMethod -Uri "https://ipkofutqtb.execute-api.us-east-1.amazonaws.com/health"
```

---

## Testing After Deployment

### Health Check
```powershell
Invoke-RestMethod -Uri "https://ipkofutqtb.execute-api.us-east-1.amazonaws.com/health"
```

### Historical Data
```powershell
Invoke-RestMethod -Uri "https://ipkofutqtb.execute-api.us-east-1.amazonaws.com/api/historical-data"
```

### Prediction (6 weeks)
```powershell
Invoke-RestMethod -Uri "https://ipkofutqtb.execute-api.us-east-1.amazonaws.com/api/predict" -Method Post -ContentType "application/json" -Body '{"horizon": 6}'
```

### Prediction (12 weeks)
```powershell
Invoke-RestMethod -Uri "https://ipkofutqtb.execute-api.us-east-1.amazonaws.com/api/predict" -Method Post -ContentType "application/json" -Body '{"horizon": 12}'
```

---

## Troubleshooting

### Docker Build Fails
- Ensure Docker is running
- Check `Dockerfile` syntax
- Verify all required files exist (models, CSV data)

### ECR Push Fails (403 Forbidden)
- Re-authenticate: `aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 463040245883.dkr.ecr.us-east-1.amazonaws.com`
- Check AWS credentials: `aws sts get-caller-identity`

### Lambda Update Fails
- Check IAM permissions
- Verify function name: `drought-predictor-api`
- Check CloudWatch logs: `aws logs tail /aws/lambda/drought-predictor-api --since 5m --region us-east-1`

### API Returns Errors After Deployment
- Wait 15-30 seconds for Lambda to fully update
- Check CloudWatch logs for errors
- Test with health endpoint first
- Verify environment variables in Lambda console

---

## Rollback

If deployment causes issues, rollback to previous image:

```powershell
# 1. List previous images
aws ecr describe-images --repository-name drought-predictor --region us-east-1

# 2. Update to previous digest
aws lambda update-function-code --function-name drought-predictor-api --image-uri 463040245883.dkr.ecr.us-east-1.amazonaws.com/drought-predictor@sha256:PREVIOUS_DIGEST --region us-east-1
```

---

## Monitoring

### View Recent Logs
```powershell
aws logs tail /aws/lambda/drought-predictor-api --since 5m --region us-east-1 --follow
```

### Check Function Status
```powershell
aws lambda get-function --function-name drought-predictor-api --region us-east-1
```

### View Metrics
- Go to AWS Console → Lambda → drought-predictor-api → Monitor tab
- Check: Invocations, Duration, Errors, Throttles

---

## Best Practices

1. **Test locally first** - Run the server locally before deploying
2. **Use version tags** - Tag images with version numbers for tracking
3. **Monitor logs** - Check CloudWatch logs after deployment
4. **Test all endpoints** - Verify health, historical data, and predictions
5. **Keep dependencies updated** - Regularly update `requirements.txt`
6. **Document changes** - Update DEPLOYMENT-SUMMARY.md with changes

---

## Related Files

- `deploy-lambda.ps1` - Automated deployment script
- `Dockerfile` - Container image definition
- `requirements.txt` - Python dependencies
- `DEPLOYMENT-SUMMARY.md` - Full deployment documentation
- `.env.example` - Environment variable template

---

## Support

For issues or questions:
1. Check CloudWatch logs first
2. Review this guide's troubleshooting section
3. Verify AWS credentials and permissions
4. Test with manual deployment steps
