#!/usr/bin/env python3
"""
Quick Query Test Script

This script tests basic queries against the loaded OCSF data.
"""

import clickhouse_connect
import os

def test_queries():
    """Test basic queries against the loaded data."""
    
    # Connect to ClickHouse
    client = clickhouse_connect.get_client(
        host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
        port=int(os.getenv('CLICKHOUSE_PORT', 8123)),
        user=os.getenv('CLICKHOUSE_USER', 'default'),
        password=os.getenv('CLICKHOUSE_PASSWORD', ''),
        database=os.getenv('CLICKHOUSE_DB', 'ocsf_data')
    )
    
    print("🔍 Testing OCSF Data Queries...")
    print("=" * 50)
    
    # Test 1: Total records
    result = client.query("SELECT count() as total_records FROM ocsf_events")
    print(f"📊 Total records: {result.result_rows[0][0]}")
    
    # Test 2: Records by file source
    result = client.query("""
        SELECT file_source, count() as record_count 
        FROM ocsf_events 
        GROUP BY file_source 
        ORDER BY record_count DESC 
        LIMIT 5
    """)
    print("\n📁 Top 5 files by record count:")
    for row in result.result_rows:
        print(f"  {row[0]}: {row[1]} records")
    
    # Test 3: Authentication events
    result = client.query("""
        SELECT timestamp, activity_name, status, src_endpoint_ip, dst_endpoint_ip
        FROM ocsf_events 
        WHERE class_name = 'Authentication'
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    print("\n🔐 Recent Authentication Events:")
    for row in result.result_rows:
        print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} -> {row[4]}")
    
    # Test 4: Failed authentication attempts
    result = client.query("""
        SELECT timestamp, activity_name, status_detail, user_name, src_endpoint_ip
        FROM ocsf_events 
        WHERE status = 'Failure' AND class_name = 'Authentication'
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    print("\n❌ Recent Failed Authentication Attempts:")
    for row in result.result_rows:
        print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
    
    print("\n✅ Query tests completed successfully!")

if __name__ == "__main__":
    test_queries() 