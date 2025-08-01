#!/usr/bin/env python3
"""
OCSF Data Loader for ClickHouse

This script analyzes the OCSF JSON data structure and loads it into ClickHouse
with an appropriate schema for efficient querying.
"""

import json
import os
import glob
import time
from typing import Dict, Any, List, Set
import clickhouse_connect
from collections import defaultdict


class OCSFDataLoader:
    def __init__(self):
        self.client = None
        self.data_path = "/data/ocsf"
        self.schema_analysis = defaultdict(set)
        self.field_types = {}
        
    def connect_to_clickhouse(self):
        """Connect to ClickHouse database."""
        try:
            self.client = clickhouse_connect.get_client(
                host=os.getenv('CLICKHOUSE_HOST', 'clickhouse'),
                port=int(os.getenv('CLICKHOUSE_PORT', 8123)),
                user=os.getenv('CLICKHOUSE_USER', 'default'),
                password=os.getenv('CLICKHOUSE_PASSWORD', ''),
                database=os.getenv('CLICKHOUSE_DB', 'ocsf_data')
            )
            print("✅ Connected to ClickHouse")
        except Exception as e:
            print(f"❌ Failed to connect to ClickHouse: {e}")
            raise
    
    def analyze_data_structure(self):
        """Analyze the structure of OCSF data to determine schema."""
        print("🔍 Analyzing OCSF data structure...")
        
        # Updated to match .log2.json files
        json_files = glob.glob(os.path.join(self.data_path, "*.log2.json"))
        print(f"Found {len(json_files)} JSON files")
        
        for file_path in json_files:
            filename = os.path.basename(file_path)
            print(f"Analyzing {filename}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        record = json.loads(line.strip())
                        self._analyze_record(record, "")
                    except json.JSONDecodeError as e:
                        print(f"Warning: JSON decode error in {filename}:{line_num}: {e}")
                        continue
        
        # Determine field types
        self._determine_field_types()
        print(f"✅ Analyzed {len(self.field_types)} fields")
    
    def _analyze_record(self, obj: Any, path: str):
        """Recursively analyze record structure."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                self.schema_analysis[current_path].add(type(value).__name__)
                self._analyze_record(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                self._analyze_record(item, current_path)
    
    def _determine_field_types(self):
        """Determine ClickHouse data types for each field."""
        for field_path, types in self.schema_analysis.items():
            if 'NoneType' in types:
                types.remove('NoneType')
            
            if not types:  # All null
                self.field_types[field_path] = 'Nullable(String)'
            elif len(types) == 1:
                type_name = list(types)[0]
                if type_name == 'str':
                    self.field_types[field_path] = 'Nullable(String)'
                elif type_name == 'int':
                    self.field_types[field_path] = 'Nullable(Int64)'
                elif type_name == 'float':
                    self.field_types[field_path] = 'Nullable(Float64)'
                elif type_name == 'bool':
                    self.field_types[field_path] = 'Nullable(UInt8)'
                else:
                    self.field_types[field_path] = 'Nullable(String)'
            else:
                # Mixed types, use String
                self.field_types[field_path] = 'Nullable(String)'
    
    def create_schema(self):
        """Create ClickHouse table schema."""
        print("📋 Creating ClickHouse schema...")
        
        # Create database if not exists
        self.client.command("CREATE DATABASE IF NOT EXISTS ocsf_data")
        
        # Drop existing table if it exists
        try:
            self.client.command("DROP TABLE IF EXISTS ocsf_events")
            print("🗑️ Dropped existing table")
        except Exception as e:
            print(f"⚠️ Warning: Could not drop existing table: {e}")
        
        # Generate CREATE TABLE statement
        fields = []
        for field_path, field_type in self.field_types.items():
            # Convert field path to column name
            column_name = field_path.replace('.', '_').replace('[', '_').replace(']', '')
            fields.append(f"`{column_name}` {field_type}")
        
        # Add metadata fields
        fields.extend([
            "`file_source` String",
            "`record_number` UInt64",
            "`timestamp` String"
        ])
        
        fields_str = ',\n            '.join(fields)
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS ocsf_events (
            {fields_str}
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, file_source, record_number)
        """
        
        try:
            self.client.command(create_table_sql)
            print("✅ Table schema created successfully")
        except Exception as e:
            print(f"❌ Failed to create schema: {e}")
            raise
    
    def load_data(self):
        """Load OCSF data into ClickHouse."""
        print("📥 Loading data into ClickHouse...")
        
        # Updated to match .log2.json files
        json_files = glob.glob(os.path.join(self.data_path, "*.log2.json"))
        total_records = 0
        
        for file_path in json_files:
            filename = os.path.basename(file_path)
            print(f"Loading {filename}...")
            
            records = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        record = json.loads(line.strip())
                        processed_record = self._process_record(record, filename, line_num)
                        records.append(processed_record)
                        
                        # Batch insert every 1000 records
                        if len(records) >= 1000:
                            self._insert_batch(records)
                            total_records += len(records)
                            records = []
                            
                    except json.JSONDecodeError as e:
                        print(f"Warning: JSON decode error in {filename}:{line_num}: {e}")
                        continue
            
            # Insert remaining records
            if records:
                self._insert_batch(records)
                total_records += len(records)
        
        print(f"✅ Loaded {total_records} records into ClickHouse")
    
    def _process_record(self, record: Dict, filename: str, record_num: int) -> Dict:
        """Process a single record for insertion."""
        processed = {}
        
        # Flatten nested structure
        self._flatten_record(record, "", processed)
        
        # Add metadata
        processed['file_source'] = filename
        processed['record_number'] = record_num
        
        # Parse timestamp
        if 'time' in processed:
            try:
                # Convert ISO timestamp to ClickHouse DateTime
                timestamp = processed['time'].replace('Z', '')
                processed['timestamp'] = timestamp
            except:
                processed['timestamp'] = '1970-01-01 00:00:00'
        else:
            processed['timestamp'] = '1970-01-01 00:00:00'
        
        return processed
    
    def _flatten_record(self, obj: Any, path: str, result: Dict):
        """Flatten nested JSON structure."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                column_name = current_path.replace('.', '_').replace('[', '_').replace(']', '')
                
                if isinstance(value, (dict, list)):
                    # Convert complex objects to JSON string
                    result[column_name] = json.dumps(value) if value else None
                else:
                    result[column_name] = value
                    
                self._flatten_record(value, current_path, result)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                self._flatten_record(item, current_path, result)
    
    def _insert_batch(self, records: List[Dict]):
        """Insert a batch of records into ClickHouse."""
        if not records:
            return
        
        # Get column names from first record
        columns = list(records[0].keys())
        
        # Prepare data for insertion
        data = []
        for record in records:
            row = [record.get(col) for col in columns]
            data.append(row)
        
        try:
            self.client.insert('ocsf_events', data, column_names=columns)
        except Exception as e:
            print(f"❌ Failed to insert batch: {e}")
            raise
    
    def create_sample_queries(self):
        """Create sample queries for demonstration."""
        print("📊 Creating sample queries...")
        
        queries = [
            {
                "name": "Total Records by File",
                "query": """
                SELECT 
                    file_source,
                    count() as record_count
                FROM ocsf_events 
                GROUP BY file_source 
                ORDER BY record_count DESC
                """
            },
            {
                "name": "Activity Types",
                "query": """
                SELECT 
                    activity_name,
                    count() as count
                FROM ocsf_events 
                WHERE activity_name IS NOT NULL
                GROUP BY activity_name 
                ORDER BY count DESC
                """
            },
            {
                "name": "Authentication Events",
                "query": """
                SELECT 
                    time,
                    activity_name,
                    status,
                    src_endpoint_ip,
                    dst_endpoint_ip
                FROM ocsf_events 
                WHERE class_name = 'Authentication'
                ORDER BY time DESC
                LIMIT 20
                """
            },
            {
                "name": "Network Activity",
                "query": """
                SELECT 
                    time,
                    activity_name,
                    src_endpoint_ip,
                    dst_endpoint_ip,
                    dst_endpoint_port
                FROM ocsf_events 
                WHERE class_name = 'DNS Activity' OR class_name = 'Network Activity'
                ORDER BY time DESC
                LIMIT 20
                """
            },
            {
                "name": "Failed Authentication Attempts",
                "query": """
                SELECT 
                    time,
                    activity_name,
                    status_detail,
                    user_name,
                    src_endpoint_ip
                FROM ocsf_events 
                WHERE status = 'Failure' AND class_name = 'Authentication'
                ORDER BY time DESC
                LIMIT 20
                """
            }
        ]
        
        # Save queries to file
        with open('/scripts/sample_queries.sql', 'w') as f:
            for query_info in queries:
                f.write(f"-- {query_info['name']}\n")
                f.write(query_info['query'])
                f.write("\n\n")
        
        print("✅ Sample queries created")
    
    def run(self):
        """Main execution method."""
        print("🚀 Starting OCSF Data Loader...")
        
        # Wait for ClickHouse to be ready
        print("⏳ Waiting for ClickHouse to be ready...")
        time.sleep(10)
        
        try:
            self.connect_to_clickhouse()
            self.analyze_data_structure()
            self.create_schema()
            self.load_data()
            self.create_sample_queries()
            print("🎉 Data loading completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during data loading: {e}")
            raise


if __name__ == "__main__":
    loader = OCSFDataLoader()
    loader.run() 