FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
# OPTIMIZATION: Install CPU-only torch first to save 800MB+ download size
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies with high timeout
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p uploads faiss_indices logs

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
