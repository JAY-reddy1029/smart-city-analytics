# Use official Python slim image — smaller size, faster startup
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (Docker layer caching optimization)
# If requirements don't change, Docker reuses this layer
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY validator.py .
COPY bigquery_writer.py .

# Run the job when container starts
CMD ["python", "main.py"]