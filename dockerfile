# Use a slim python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only necessary build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Healthcheck to let Portainer know when the app is actually ready
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the app
ENTRYPOINT ["streamlit", "run", "health_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]