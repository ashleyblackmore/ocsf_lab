-- Network Traffic Analysis: Bytes Transferred by IP and Host
-- OCSF Data Analysis Queries

-- 1. Network Activity Bytes Transferred by Source IP
SELECT 
    src_endpoint_ip,
    COUNT(*) as connection_count,
    SUM(traffic_bytes_in) as total_bytes_in,
    SUM(traffic_bytes_out) as total_bytes_out,
    SUM(traffic_bytes_in + traffic_bytes_out) as total_bytes_transferred,
    AVG(traffic_bytes_in) as avg_bytes_in,
    AVG(traffic_bytes_out) as avg_bytes_out
FROM ocsf_data.ocsf_events 
WHERE class_name = 'Network Activity' 
    AND traffic_bytes_in IS NOT NULL 
    AND traffic_bytes_out IS NOT NULL
GROUP BY src_endpoint_ip
ORDER BY total_bytes_transferred DESC
LIMIT 20;

-- 2. Network Activity Bytes Transferred by Destination IP
SELECT 
    dst_endpoint_ip,
    COUNT(*) as connection_count,
    SUM(traffic_bytes_in) as total_bytes_in,
    SUM(traffic_bytes_out) as total_bytes_out,
    SUM(traffic_bytes_in + traffic_bytes_out) as total_bytes_transferred,
    AVG(traffic_bytes_in) as avg_bytes_in,
    AVG(traffic_bytes_out) as avg_bytes_out
FROM ocsf_data.ocsf_events 
WHERE class_name = 'Network Activity' 
    AND traffic_bytes_in IS NOT NULL 
    AND traffic_bytes_out IS NOT NULL
GROUP BY dst_endpoint_ip
ORDER BY total_bytes_transferred DESC
LIMIT 20;

-- 3. Bytes Transferred by Source and Destination IP Pair
SELECT 
    src_endpoint_ip,
    dst_endpoint_ip,
    COUNT(*) as connection_count,
    SUM(traffic_bytes_in) as total_bytes_in,
    SUM(traffic_bytes_out) as total_bytes_out,
    SUM(traffic_bytes_in + traffic_bytes_out) as total_bytes_transferred,
    connection_info_protocol_name as protocol
FROM ocsf_data.ocsf_events 
WHERE class_name = 'Network Activity' 
    AND traffic_bytes_in IS NOT NULL 
    AND traffic_bytes_out IS NOT NULL
GROUP BY src_endpoint_ip, dst_endpoint_ip, connection_info_protocol_name
ORDER BY total_bytes_transferred DESC
LIMIT 30;

-- 4. File Transfer Analysis by IP (SMB and File Hosting)
SELECT 
    src_endpoint_ip,
    dst_endpoint_ip,
    file_name,
    file_size,
    file_type,
    activity_name,
    COUNT(*) as transfer_count
FROM ocsf_data.ocsf_events 
WHERE (class_name LIKE '%SMB%' OR class_name LIKE '%File%')
    AND file_size IS NOT NULL
    AND file_size > 0
GROUP BY src_endpoint_ip, dst_endpoint_ip, file_name, file_size, file_type, activity_name
ORDER BY file_size DESC
LIMIT 20;

-- 5. Total Bytes by Host and Protocol
SELECT 
    src_endpoint_ip as host_ip,
    connection_info_protocol_name as protocol,
    COUNT(*) as connection_count,
    SUM(traffic_bytes_in) as total_bytes_in,
    SUM(traffic_bytes_out) as total_bytes_out,
    SUM(traffic_bytes_in + traffic_bytes_out) as total_bytes_transferred,
    ROUND(SUM(traffic_bytes_in + traffic_bytes_out) / 1024 / 1024, 2) as total_mb_transferred
FROM ocsf_data.ocsf_events 
WHERE class_name = 'Network Activity' 
    AND traffic_bytes_in IS NOT NULL 
    AND traffic_bytes_out IS NOT NULL
    AND connection_info_protocol_name IS NOT NULL
GROUP BY src_endpoint_ip, connection_info_protocol_name
ORDER BY total_bytes_transferred DESC
LIMIT 30;

-- 6. Hourly Bytes Transferred by IP
SELECT 
    src_endpoint_ip,
    toStartOfHour(parseDateTimeBestEffort(time)) as hour,
    COUNT(*) as connection_count,
    SUM(traffic_bytes_in + traffic_bytes_out) as total_bytes_transferred,
    ROUND(SUM(traffic_bytes_in + traffic_bytes_out) / 1024 / 1024, 2) as total_mb_transferred
FROM ocsf_data.ocsf_events 
WHERE class_name = 'Network Activity' 
    AND traffic_bytes_in IS NOT NULL 
    AND traffic_bytes_out IS NOT NULL
    AND parseDateTimeBestEffort(time) >= now() - INTERVAL 24 HOUR
GROUP BY src_endpoint_ip, hour
ORDER BY hour DESC, total_bytes_transferred DESC
LIMIT 50;

-- 7. Top Data Transfer Hosts (Summary)
SELECT 
    src_endpoint_ip as host_ip,
    COUNT(DISTINCT dst_endpoint_ip) as unique_destinations,
    COUNT(*) as total_connections,
    SUM(traffic_bytes_in + traffic_bytes_out) as total_bytes_transferred,
    ROUND(SUM(traffic_bytes_in + traffic_bytes_out) / 1024 / 1024, 2) as total_mb_transferred,
    ROUND(SUM(traffic_bytes_in + traffic_bytes_out) / 1024 / 1024 / 1024, 2) as total_gb_transferred,
    MIN(parseDateTimeBestEffort(time)) as first_connection,
    MAX(parseDateTimeBestEffort(time)) as last_connection
FROM ocsf_data.ocsf_events 
WHERE class_name = 'Network Activity' 
    AND traffic_bytes_in IS NOT NULL 
    AND traffic_bytes_out IS NOT NULL
GROUP BY src_endpoint_ip
ORDER BY total_bytes_transferred DESC
LIMIT 15;

-- 8. Anomalous Data Transfer Detection
SELECT 
    src_endpoint_ip,
    COUNT(*) as connection_count,
    SUM(traffic_bytes_in + traffic_bytes_out) as total_bytes_transferred,
    ROUND(SUM(traffic_bytes_in + traffic_bytes_out) / 1024 / 1024, 2) as total_mb_transferred,
    AVG(traffic_bytes_in + traffic_bytes_out) as avg_bytes_per_connection,
    MAX(traffic_bytes_in + traffic_bytes_out) as max_bytes_per_connection
FROM ocsf_data.ocsf_events 
WHERE class_name = 'Network Activity' 
    AND traffic_bytes_in IS NOT NULL 
    AND traffic_bytes_out IS NOT NULL
GROUP BY src_endpoint_ip
HAVING total_bytes_transferred > 1000000  -- More than 1MB total
    OR avg_bytes_per_connection > 100000   -- More than 100KB average per connection
ORDER BY total_bytes_transferred DESC
LIMIT 20;

-- 9. File Transfer Summary by Host
SELECT 
    src_endpoint_ip as host_ip,
    COUNT(DISTINCT file_name) as unique_files,
    COUNT(*) as total_transfers,
    SUM(file_size) as total_file_size_bytes,
    ROUND(SUM(file_size) / 1024 / 1024, 2) as total_file_size_mb,
    AVG(file_size) as avg_file_size_bytes,
    MAX(file_size) as largest_file_bytes
FROM ocsf_data.ocsf_events 
WHERE (class_name LIKE '%SMB%' OR class_name LIKE '%File%')
    AND file_size IS NOT NULL 
    AND file_size > 0
GROUP BY src_endpoint_ip
ORDER BY total_file_size_bytes DESC
LIMIT 15;

-- 10. Network Traffic by Time Period
SELECT 
    toStartOfHour(parseDateTimeBestEffort(time)) as hour,
    src_endpoint_ip,
    COUNT(*) as connection_count,
    SUM(traffic_bytes_in + traffic_bytes_out) as total_bytes_transferred,
    ROUND(SUM(traffic_bytes_in + traffic_bytes_out) / 1024 / 1024, 2) as total_mb_transferred
FROM ocsf_data.ocsf_events 
WHERE class_name = 'Network Activity' 
    AND traffic_bytes_in IS NOT NULL 
    AND traffic_bytes_out IS NOT NULL
    AND parseDateTimeBestEffort(time) >= now() - INTERVAL 7 DAY
GROUP BY hour, src_endpoint_ip
ORDER BY hour DESC, total_bytes_transferred DESC
LIMIT 100; 