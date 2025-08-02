# OCSF Security Analysis Lab

Welcome to the OCSF (Open Cybersecurity Schema Framework) Security Analysis Lab! This environment provides a complete setup for analyzing cybersecurity data using ClickHouse and modern web-based tools.

## 🚀 Quick Start

### Prerequisites

#### 1. Install Docker Desktop

**Download Docker Desktop:**
- **macOS**: https://www.docker.com/products/docker-desktop/
- **Windows**: https://www.docker.com/products/docker-desktop/
- **Linux**: https://docs.docker.com/desktop/install/linux-install/

**Installation Steps:**
1. Download Docker Desktop for your operating system
2. Run the installer and follow the setup wizard
3. Start Docker Desktop
4. Verify installation by opening a terminal and running: `docker --version`

#### 2. Verify Docker Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Verify Docker is running
docker info
```

### Starting the Lab

#### Option 1: Automated Start (Recommended)
```bash
# Make the script executable (first time only)
chmod +x start_analysis.sh

# Start the lab
./start_analysis.sh
```

#### Option 2: Manual Start
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

## 🌐 Access Points

Once the lab is running, you can access the following services:

### Primary Analysis Tools

| Service | URL | Description |
|---------|-----|-------------|
| **CH-UI** | http://localhost:5521 | Modern ClickHouse web interface with IntelliSense |
| **ClickHouse HTTP** | http://localhost:8123 | ClickHouse HTTP interface |
| **ClickHouse Native** | localhost:9000 | ClickHouse native protocol |

### Service Details

#### CH-UI (ClickHouse User Interface)
- **URL**: http://localhost:5521
- **Features**: 
  - Modern web-based SQL editor
  - IntelliSense and auto-completion
  - Query history and favorites
  - Export results to CSV/JSON
  - Table browser and schema explorer
  - Real-time query execution

#### ClickHouse Database
- **HTTP Interface**: http://localhost:8123
- **Native Protocol**: localhost:9000
- **Database**: `ocsf_data`
- **Default User**: `default` (no password)

## 📊 Data Overview

The lab includes **2,834 OCSF events** across multiple security event types:

- **Authentication Events**: Kerberos, LDAP, LDAP Search
- **Network Activity**: DNS, HTTP, SSL, X509, DCE-RPC, Connections
- **File Activity**: File hosting, SMB file operations, SMB mapping
- **Detection Findings**: Security alerts and findings
- **System Activity**: DHCP, NTP, and other system events

## 🔍 Getting Started with Analysis

### 1. Open CH-UI
Navigate to http://localhost:5521 in your web browser.

### 2. Basic Queries to Start With

```sql
-- Count total events
SELECT COUNT(*) FROM ocsf_events;

-- View event types distribution
SELECT class_name, COUNT(*) as event_count 
FROM ocsf_events 
GROUP BY class_name 
ORDER BY event_count DESC;

-- Recent authentication events
SELECT timestamp, activity_name, status, src_endpoint_ip, user_name
FROM ocsf_events 
WHERE class_name = 'Authentication'
ORDER BY timestamp DESC
LIMIT 10;

-- Failed authentication attempts
SELECT timestamp, activity_name, user_name, src_endpoint_ip, status_detail
FROM ocsf_events 
WHERE class_name = 'Authentication' AND status = 'Failure'
ORDER BY timestamp DESC
LIMIT 10;
```

### 3. Sample Analysis Queries

#### Security Analysis
```sql
-- Authentication success rate by type
SELECT 
    activity_name,
    COUNT(*) as total_attempts,
    COUNT(CASE WHEN status = 'Success' THEN 1 END) as successful,
    ROUND(COUNT(CASE WHEN status = 'Success' THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
FROM ocsf_events 
WHERE class_name = 'Authentication'
GROUP BY activity_name
ORDER BY total_attempts DESC;
```

#### Network Analysis
```sql
-- Top source IPs by activity
SELECT 
    src_endpoint_ip,
    COUNT(*) as event_count,
    COUNT(DISTINCT class_name) as unique_event_types
FROM ocsf_events 
WHERE src_endpoint_ip IS NOT NULL
GROUP BY src_endpoint_ip
ORDER BY event_count DESC
LIMIT 20;
```

#### Timeline Analysis
```sql
-- Events by hour
SELECT 
    toStartOfHour(timestamp) as hour,
    COUNT(*) as event_count
FROM ocsf_events 
GROUP BY hour
ORDER BY hour;
```

## 📁 Project Structure

```
ocsf_lab/
├── docker-compose.yml          # Docker services configuration
├── start_analysis.sh           # Automated startup script
├── Dockerfile                  # Data loader container
├── data/                       # Data directory
├── init/                       # Database initialization
├── scripts/                    # Analysis scripts
│   ├── load_data.py           # Data loading script
│   ├── query_examples.py      # Query examples
│   ├── run_queries.py         # Query runner
│   └── sample_queries.sql     # Sample SQL queries
├── OCSF_data_cleaned/         # Cleaned OCSF data files
│   ├── Authentication_*.log2.json
│   ├── Network_Activity_*.log2.json
│   ├── File_Hosting_*.log2.json
│   └── ...
└── README.md                   # This file
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Docker Not Running
```bash
# Start Docker Desktop
# On macOS: Open Docker Desktop app
# On Windows: Start Docker Desktop from Start Menu
# On Linux: sudo systemctl start docker
```

#### 2. Port Already in Use
```bash
# Check what's using the ports
lsof -i :5521  # CH-UI
lsof -i :8123  # ClickHouse HTTP
lsof -i :9000  # ClickHouse Native

# Stop conflicting services or change ports in docker-compose.yml
```

#### 3. Services Not Starting
```bash
# Check service logs
docker-compose logs clickhouse
docker-compose logs ch-ui
docker-compose logs data-loader

# Restart services
docker-compose down
docker-compose up -d
```

#### 4. Data Not Loading
```bash
# Check if data files exist
ls -la OCSF_data_cleaned/

# Re-run data loader
docker-compose restart data-loader
```

### Service Health Checks

```bash
# Check if ClickHouse is responding
curl http://localhost:8123/ping

# Check if CH-UI is accessible
curl http://localhost:5521

# View all running containers
docker-compose ps
```

## 📚 Additional Resources

### Documentation Files
- `scripts/sample_queries.sql` - Comprehensive query examples
- `scripts/query_examples.py` - Python query examples
- `ch_ui_guide.md` - CH-UI usage guide

### Useful Commands

```bash
# View service logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart clickhouse

# Access ClickHouse CLI
docker-compose exec clickhouse clickhouse-client

# Backup data
docker-compose exec clickhouse clickhouse-client --query "BACKUP TABLE ocsf_events TO '/backup'"
```

## 🔧 Configuration

### Environment Variables
The lab uses these default configurations:
- **ClickHouse Database**: `ocsf_data`
- **ClickHouse User**: `default`
- **ClickHouse Password**: (empty)
- **CH-UI Port**: `5521`
- **ClickHouse HTTP Port**: `8123`
- **ClickHouse Native Port**: `9000`

### Customizing the Setup
Edit `docker-compose.yml` to:
- Change ports
- Modify ClickHouse settings
- Add additional services
- Configure volumes

## 🎯 Use Cases

### Security Analysis
- Monitor authentication patterns
- Detect failed login attempts
- Track user activity
- Identify suspicious behavior

### Network Monitoring
- Analyze traffic patterns
- Monitor DNS queries
- Track HTTP activity
- Identify top talkers

### Compliance Reporting
- Generate activity reports
- Track file access patterns
- Monitor user behavior
- Document security events

## 🤝 Contributing

To extend the lab:
1. Add new data files to `OCSF_data_cleaned/`
2. Create new analysis scripts in `scripts/`
3. Update `docker-compose.yml` for new services
4. Document changes in this README

## 📄 License

This project is part of the OCSF Lab environment for cybersecurity data analysis and education.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Verify Docker Desktop is running
4. Check port availability
5. Ensure data files are present in `OCSF_data_cleaned/`

---

**Happy Analyzing! 🚀** 