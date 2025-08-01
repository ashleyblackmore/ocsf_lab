#!/usr/bin/env python3
"""
OCSF Data Query Examples

This script provides example queries for analyzing the OCSF data in ClickHouse.
"""

import clickhouse_connect
import os
import pandas as pd
from datetime import datetime


class OCSFQueryExamples:
    def __init__(self):
        self.client = None
        
    def connect_to_clickhouse(self):
        """Connect to ClickHouse database."""
        try:
            self.client = clickhouse_connect.get_client(
                host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
                port=int(os.getenv('CLICKHOUSE_PORT', 8123)),
                user=os.getenv('CLICKHOUSE_USER', 'default'),
                password=os.getenv('CLICKHOUSE_PASSWORD', ''),
                database=os.getenv('CLICKHOUSE_DB', 'ocsf_data')
            )
            print("✅ Connected to ClickHouse")
        except Exception as e:
            print(f"❌ Failed to connect to ClickHouse: {e}")
            raise
    
    def run_query(self, query: str, description: str = ""):
        """Run a query and display results."""
        print(f"\n🔍 {description}")
        print("=" * 50)
        print(query)
        print("-" * 50)
        
        try:
            result = self.client.query(query)
            df = pd.DataFrame(result.result_rows, columns=result.column_names)
            print(df.to_string(index=False))
            print(f"\n📊 Found {len(df)} rows")
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    def run_examples(self):
        """Run example queries."""
        print("🚀 Running OCSF Data Query Examples...")
        
        # 1. Overview of data
        self.run_query(
            "SELECT count() as total_records FROM ocsf_events",
            "Total Records in Dataset"
        )
        
        # 2. Records by file source
        self.run_query(
            """
            SELECT 
                file_source,
                count() as record_count
            FROM ocsf_events 
            GROUP BY file_source 
            ORDER BY record_count DESC
            """,
            "Records by File Source"
        )
        
        # 3. Activity types distribution
        self.run_query(
            """
            SELECT 
                activity_name,
                count() as count
            FROM ocsf_events 
            WHERE activity_name IS NOT NULL
            GROUP BY activity_name 
            ORDER BY count DESC
            """,
            "Activity Types Distribution"
        )
        
        # 4. Authentication events
        self.run_query(
            """
            SELECT 
                timestamp,
                activity_name,
                status,
                src_endpoint_ip,
                dst_endpoint_ip,
                user_name
            FROM ocsf_events 
            WHERE class_name = 'Authentication'
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            "Recent Authentication Events"
        )
        
        # 5. Failed authentication attempts
        self.run_query(
            """
            SELECT 
                timestamp,
                activity_name,
                status_detail,
                user_name,
                src_endpoint_ip
            FROM ocsf_events 
            WHERE status = 'Failure' AND class_name = 'Authentication'
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            "Failed Authentication Attempts"
        )
        
        # 6. Network activity
        self.run_query(
            """
            SELECT 
                timestamp,
                activity_name,
                src_endpoint_ip,
                dst_endpoint_ip,
                dst_endpoint_port
            FROM ocsf_events 
            WHERE class_name IN ('DNS Activity', 'Network Activity')
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            "Recent Network Activity"
        )
        
        # 7. DNS queries
        self.run_query(
            """
            SELECT 
                timestamp,
                query_hostname,
                rcode,
                src_endpoint_ip,
                dst_endpoint_ip
            FROM ocsf_events 
            WHERE class_name = 'DNS Activity' AND query_hostname IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            "Recent DNS Queries"
        )
        
        # 8. HTTP activity
        self.run_query(
            """
            SELECT 
                timestamp,
                http_request_http_method,
                http_request_url_hostname,
                http_response_code,
                src_endpoint_ip,
                dst_endpoint_ip
            FROM ocsf_events 
            WHERE class_name = 'HTTP Activity'
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            "Recent HTTP Activity"
        )
        
        # 9. File activity
        self.run_query(
            """
            SELECT 
                timestamp,
                file_name,
                file_size,
                file_type,
                src_endpoint_ip
            FROM ocsf_events 
            WHERE file_name IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            "Recent File Activity"
        )
        
        # 10. Top source IPs
        self.run_query(
            """
            SELECT 
                src_endpoint_ip,
                count() as event_count
            FROM ocsf_events 
            WHERE src_endpoint_ip IS NOT NULL
            GROUP BY src_endpoint_ip
            ORDER BY event_count DESC
            LIMIT 10
            """,
            "Top Source IP Addresses"
        )
        
        # 11. Top destination IPs
        self.run_query(
            """
            SELECT 
                dst_endpoint_ip,
                count() as event_count
            FROM ocsf_events 
            WHERE dst_endpoint_ip IS NOT NULL
            GROUP BY dst_endpoint_ip
            ORDER BY event_count DESC
            LIMIT 10
            """,
            "Top Destination IP Addresses"
        )
        
        # 12. Events by severity
        self.run_query(
            """
            SELECT 
                severity,
                count() as count
            FROM ocsf_events 
            WHERE severity IS NOT NULL
            GROUP BY severity
            ORDER BY count DESC
            """,
            "Events by Severity"
        )
        
        # 13. Timeline analysis
        self.run_query(
            """
            SELECT 
                toDate(timestamp) as date,
                count() as events
            FROM ocsf_events 
            GROUP BY date
            ORDER BY date
            """,
            "Events Timeline (Daily)"
        )
        
        # 14. Service analysis
        self.run_query(
            """
            SELECT 
                service_name,
                count() as count
            FROM ocsf_events 
            WHERE service_name IS NOT NULL
            GROUP BY service_name
            ORDER BY count DESC
            LIMIT 10
            """,
            "Top Services"
        )
        
        # 15. User activity
        self.run_query(
            """
            SELECT 
                user_name,
                count() as count
            FROM ocsf_events 
            WHERE user_name IS NOT NULL
            GROUP BY user_name
            ORDER BY count DESC
            LIMIT 10
            """,
            "Top Users by Activity"
        )
    
    def run_custom_query(self, query: str):
        """Run a custom query."""
        print(f"\n🔍 Custom Query")
        print("=" * 50)
        print(query)
        print("-" * 50)
        
        try:
            result = self.client.query(query)
            df = pd.DataFrame(result.result_rows, columns=result.column_names)
            print(df.to_string(index=False))
            print(f"\n📊 Found {len(df)} rows")
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    def run(self):
        """Main execution method."""
        try:
            self.connect_to_clickhouse()
            self.run_examples()
            print("\n🎉 Query examples completed!")
            
        except Exception as e:
            print(f"❌ Error during query execution: {e}")
            raise


if __name__ == "__main__":
    examples = OCSFQueryExamples()
    examples.run() 