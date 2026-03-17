FROM python:3.10-slim

WORKDIR /app

# Install system deps (weasyprint, kaleido/chromium)
RUN apt-get update && apt-get install -y \
    build-essential \
    chromium \
    chromium-driver \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libffi-dev \
    libgdk-pixbuf2.0-0 \
    libxml2 \
    libxmlsec1-dev \
    libcairo2 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "health_dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]