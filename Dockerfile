FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    clickhouse-connect \
    pandas \
    numpy

# Create directories
RUN mkdir -p /scripts /data

# Set working directory
WORKDIR /scripts

# Copy scripts
COPY scripts/ .

# Make scripts executable
RUN chmod +x *.py

# Default command
CMD ["python3", "load_data.py"] 