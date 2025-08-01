#!/bin/bash

# OCSF Data Analysis Startup Script
# This script starts the Docker environment and provides analysis tools

set -e

echo "🚀 Starting OCSF Data Analysis Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if data directory exists
if [ ! -d "OCSF_data_cleaned" ]; then
    print_error "OCSF_data_cleaned directory not found. Please run the data cleaning script first."
    exit 1
fi

print_header "Starting Docker Services"

# Start the Docker services
print_status "Starting ClickHouse, Tabix, and Data Loader..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 15

# Check if services are running
print_status "Checking service status..."
docker-compose ps

print_header "Data Loading Status"

# Check if data is loaded
print_status "Checking if data is loaded..."
sleep 5

# Try to query the database
if curl -s "http://localhost:8123/?query=SELECT%20count()%20FROM%20ocsf_data.ocsf_events" > /dev/null 2>&1; then
    RECORD_COUNT=$(curl -s "http://localhost:8123/?query=SELECT%20count()%20FROM%20ocsf_data.ocsf_events" | tail -n 1)
    print_status "Data loaded successfully! Found $RECORD_COUNT records."
else
    print_warning "Data may not be fully loaded yet. This is normal for the first run."
    print_status "You can check the loading progress with: docker-compose logs data-loader"
fi

print_header "Access Information"

echo -e "${GREEN}Web Interface:${NC} http://localhost:8080"
echo -e "${GREEN}ClickHouse HTTP:${NC} http://localhost:8123"
echo -e "${GREEN}ClickHouse Native:${NC} localhost:9000"

print_header "Quick Analysis Commands"

echo -e "${YELLOW}Run example queries:${NC}"
echo "docker exec -it ocsf_data_loader python3 /scripts/query_examples.py"
echo ""
echo -e "${YELLOW}Check service logs:${NC}"
echo "docker-compose logs -f"
echo ""
echo -e "${YELLOW}Stop services:${NC}"
echo "docker-compose down"
echo ""
echo -e "${YELLOW}Restart services:${NC}"
echo "docker-compose restart"

print_header "Sample Queries"

echo -e "${YELLOW}Total records:${NC}"
echo "curl 'http://localhost:8123/?query=SELECT%20count()%20FROM%20ocsf_data.ocsf_events'"
echo ""
echo -e "${YELLOW}Authentication events:${NC}"
echo "curl 'http://localhost:8123/?query=SELECT%20timestamp,activity_name,status%20FROM%20ocsf_data.ocsf_events%20WHERE%20class_name%20%3D%20%27Authentication%27%20ORDER%20BY%20timestamp%20DESC%20LIMIT%205'"
echo ""
echo -e "${YELLOW}Failed authentication attempts:${NC}"
echo "curl 'http://localhost:8123/?query=SELECT%20timestamp,activity_name,status_detail,user_name%20FROM%20ocsf_data.ocsf_events%20WHERE%20status%20%3D%20%27Failure%27%20AND%20class_name%20%3D%20%27Authentication%27%20ORDER%20BY%20timestamp%20DESC%20LIMIT%205'"

print_header "Next Steps"

echo "1. Open http://localhost:8080 in your browser"
echo "2. Use the SQL interface to explore your data"
echo "3. Run the example queries script for comprehensive analysis"
echo "4. Create custom visualizations and dashboards"

print_status "Environment is ready! 🎉"

# Optional: Run example queries
read -p "Would you like to run example queries now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_header "Running Example Queries"
    docker exec -it ocsf_data_loader python3 /scripts/query_examples.py
fi

print_status "Setup complete! Happy analyzing! 📊" 