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
ENV PORT=8000

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port 8000 (Koyeb default)
EXPOSE 8000

# Run Streamlit - use PORT env var (Koyeb sets this to 8000)
CMD streamlit run app.py --server.port=${PORT:-8000} --server.address=0.0.0.0
