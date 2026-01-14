FROM python:3.9-slim

# Install system dependencies including Chrome/Chromium
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    chromium-sandbox \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome binary location
ENV CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
