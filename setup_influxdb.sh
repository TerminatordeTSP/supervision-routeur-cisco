#!/bin/bash

# InfluxDB Setup Script for Router Supervision Project
# This script helps set up InfluxDB and creates basic dashboards

echo "🚀 Setting up InfluxDB for Router Supervision..."

# Check if InfluxDB is running
echo "Checking InfluxDB status..."
if curl -s http://localhost:8086/health > /dev/null 2>&1; then
    echo "✅ InfluxDB is running!"
else
    echo "❌ InfluxDB is not running. Please start it first with:"
    echo "   docker-compose up -d influxdb"
    exit 1
fi

# Configuration
INFLUXDB_URL="http://localhost:8086"
INFLUXDB_TOKEN="my-super-secret-auth-token"
INFLUXDB_ORG="telecom-sudparis"
INFLUXDB_BUCKET="router-metrics"

echo "📊 Creating basic InfluxDB setup..."

# Check if bucket exists
echo "Checking if bucket exists..."
if influx bucket list --org "$INFLUXDB_ORG" --token "$INFLUXDB_TOKEN" --host "$INFLUXDB_URL" | grep -q "$INFLUXDB_BUCKET"; then
    echo "✅ Bucket '$INFLUXDB_BUCKET' already exists"
else
    echo "📦 Creating bucket '$INFLUXDB_BUCKET'..."
    influx bucket create \
        --name "$INFLUXDB_BUCKET" \
        --org "$INFLUXDB_ORG" \
        --token "$INFLUXDB_TOKEN" \
        --host "$INFLUXDB_URL" \
        --retention 168h  # 7 days retention
    echo "✅ Bucket created successfully"
fi

# Create a simple dashboard template
echo "📈 Creating dashboard template..."
cat > /tmp/router-dashboard.json << 'EOF'
{
  "meta": {
    "version": "1",
    "type": "dashboard",
    "name": "Router Monitoring Dashboard",
    "description": "Dashboard for monitoring Cisco router metrics"
  },
  "content": {
    "data": {
      "type": "dashboard",
      "attributes": {
        "name": "Router Monitoring Dashboard",
        "description": "Dashboard for monitoring Cisco router metrics"
      }
    }
  }
}
EOF

echo "✅ Dashboard template created at /tmp/router-dashboard.json"

# Show connection info
echo ""
echo "🔗 InfluxDB Connection Information:"
echo "   URL: $INFLUXDB_URL"
echo "   Organization: $INFLUXDB_ORG"
echo "   Bucket: $INFLUXDB_BUCKET"
echo "   Token: $INFLUXDB_TOKEN"
echo ""
echo "🌐 Access InfluxDB UI at: http://localhost:8086"
echo "   Username: admin"
echo "   Password: admin123456"
echo ""
echo "🐍 Test the Python client:"
echo "   python3 influxdb_client.py"
echo ""
echo "📊 Query data with Django management command:"
echo "   python router_supervisor/manage.py query_influxdb --help"
echo ""
echo "✅ Setup completed successfully!"
