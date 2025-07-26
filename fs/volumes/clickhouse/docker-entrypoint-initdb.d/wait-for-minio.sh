#!/bin/bash

echo "Waiting for MinIO to be ready..."
until curl -f http://minio:10000/minio/health/live > /dev/null 2>&1; do
    echo "MinIO is not ready yet, waiting..."
    sleep 5
done
echo "MinIO is ready!" 