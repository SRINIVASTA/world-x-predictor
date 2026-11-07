# Use a lightweight official Python baseline engine image
FROM python:3.11-slim

# Install system dependencies required by WeasyPrint (Pango, Cairo, GObject)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libgobject-2.0-0 \
    libcairo2 \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory contexts
WORKDIR /app

# Copy requirement files first to utilize build layer caching optimizations
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all remaining source application tree code
COPY . .

# Expose standard Streamlit communication port allocations
EXPOSE 8501

# Run the live engine using execution array arguments
CMD ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
