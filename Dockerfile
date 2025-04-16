# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data models

# Expose ports
EXPOSE 8000 8501

# Start both FastAPI and Streamlit
CMD ["sh", "-c", "streamlit run dashboard/dashboard.py --server.port 8501 & uvicorn app.main:app --host 0.0.0.0 --port 8000"] 