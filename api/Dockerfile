# For the Python base image
FROM python:3.9-slim as python-base

ENV PYTHONUNBUFFERED=1

# Set a directory for the app
WORKDIR /api

# Install system dependencies required for mysqlclient
# You need build-essential, default-libmysqlclient-dev and python3-dev
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    python3-dev \
    pkg-config \
 && rm -rf /var/lib/apt/lists/*



RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . . 



