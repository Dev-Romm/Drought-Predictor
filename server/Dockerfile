# Dockerfile for AWS Lambda deployment of Drought Predictor Backend
# Uses AWS Lambda Python 3.10 base image (Requirement 11.1)

FROM public.ecr.aws/lambda/python:3.10

# Working directory is already set to /var/task in Lambda base image

# Install system dependencies required for Prophet
RUN yum update -y && yum install -y \
    gcc \
    gcc-c++ \
    gcc-gfortran \
    openblas-devel \
    lapack-devel \
    && yum clean all

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install Python dependencies in stages to handle large packages
# (Requirement 11.5)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install numpy first (required by many other packages)
RUN pip install --no-cache-dir numpy==1.26.3

# Install core dependencies
RUN pip install --no-cache-dir \
    pandas==2.2.0 \
    scikit-learn==1.4.0 \
    numpy==1.26.3

# Install Prophet and its dependencies
RUN pip install --no-cache-dir \
    cmdstanpy==1.2.1 \
    prophet==1.1.5

# Install FastAPI and web framework dependencies
RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    mangum==0.17.0 \
    python-multipart==0.0.6 \
    python-dotenv==1.0.0 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0

# Copy server code into container
COPY *.py ${LAMBDA_TASK_ROOT}/

# Copy models directory into container (Prophet model only)
COPY models/ndvi_prophet_model.pkl ${LAMBDA_TASK_ROOT}/models/ndvi_prophet_model.pkl

# Copy CSV data file into container
COPY turkana_ndvi_csv_biweekly.csv ${LAMBDA_TASK_ROOT}/turkana_ndvi_csv_biweekly.csv

# Set environment variables
ENV CSV_PATH=turkana_ndvi_csv_biweekly.csv
ENV PROPHET_MODEL_PATH=models/ndvi_prophet_model.pkl
ENV FRONTEND_URL=*
ENV PYTHONUNBUFFERED=1

# Set CMD to Lambda handler using Mangum (Requirement 11.2)
# The handler function is defined in main.py as 'handler = Mangum(app)'
CMD ["main.handler"]
