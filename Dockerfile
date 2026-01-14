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

# Expose port (Koyeb uses PORT env var, defaults to 8000)
EXPOSE 8000

# Create startup script that uses PORT env var
RUN echo '#!/bin/bash\n\
export PORT=${PORT:-8000}\n\
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0' > /start.sh && \
    chmod +x /start.sh

# Run Streamlit using PORT from environment
CMD ["/start.sh"]
