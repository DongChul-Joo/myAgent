FROM python:3.9-slim-buster as builder

# Install build dependencies
RUN apt-get update \
    && apt-get install -y build-essential pkg-config libmariadb-dev libgl1-mesa-glx poppler-utils tesseract-ocr libtesseract-dev\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt