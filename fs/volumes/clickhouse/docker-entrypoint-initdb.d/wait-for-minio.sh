#!/bin/bash

echo "Waiting for MinIO to be ready..."
until wget -q --spider http://minio:10000/minio/health/live; do
    echo "MinIO is not ready yet, waiting..."
    sleep 5
done
echo "MinIO is ready!" 