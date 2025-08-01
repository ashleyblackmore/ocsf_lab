#!/bin/bash

echo "🚀 Starting OCSF Security Analysis Environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start the services
echo "📦 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ OCSF Analysis Environment is ready!"
echo ""
echo "🌐 Access Points:"
echo "   • CH-UI (ClickHouse UI): http://localhost:5521"
echo "   • ClickHouse HTTP:  http://localhost:8123"
echo "   • ClickHouse Native: localhost:9000"
echo ""
echo "📈 Analysis Tools:"
echo "   • CH-UI: Modern ClickHouse web interface with IntelliSense"
echo "   • Chat2DB: AI-powered SQL client with ClickHouse support"
echo "   • Grafana: Pre-configured dashboards for OCSF data"
echo "   • 2834 OCSF events are loaded and ready for analysis"
echo ""
echo "🔍 Quick Start with CH-UI:"
echo "   1. Open http://localhost:5521"
echo "   2. CH-UI automatically connects to ClickHouse"
echo "   3. Start with basic queries:"
echo "      - SELECT COUNT(*) FROM ocsf_data.ocsf_events"
echo "      - SELECT class_name, count() FROM ocsf_data.ocsf_events GROUP BY class_name"
echo "   4. Use IntelliSense for auto-completion"
echo "   5. Export results for reporting"
echo ""
echo "📚 Sample Queries:"
echo "   • SELECT COUNT(*) FROM ocsf_events"
echo "   • SELECT class_name, count() FROM ocsf_events GROUP BY class_name"
echo "   • SELECT * FROM ocsf_events WHERE class_name = 'Authentication' LIMIT 10"
echo ""
echo "📖 Documentation:"
echo "   • CH-UI Guide: ch_ui_guide.md"
echo "   • Sample Queries: scripts/sample_queries.sql" 