#!/usr/bin/env python3
"""
OCSF Data Cleaner

This script processes OCSF JSON files and removes fields that are always null,
while keeping fields that have at least one non-null value.
"""

import json
import os
import glob
from collections import defaultdict
from typing import Dict, Set, Any, List
import argparse


def analyze_null_fields(data_dir: str) -> Dict[str, Set[str]]:
    """
    Analyze all JSON files in the directory to find which fields are always null
    vs. fields that have at least one non-null value.
    
    Returns:
        Dict with 'always_null' and 'sometimes_null' field sets
    """
    always_null_fields = set()
    sometimes_null_fields = set()
    field_values = defaultdict(set)
    
    # Get all JSON files in the directory
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    print(f"Analyzing {len(json_files)} JSON files...")
    
    for file_path in json_files:
        print(f"Processing {os.path.basename(file_path)}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line.strip())
                    _collect_field_info(record, field_values, "")
                except json.JSONDecodeError as e:
                    print(f"Warning: JSON decode error in {file_path}:{line_num}: {e}")
                    continue
    
    # Analyze which fields are always null vs sometimes null
    for field_path, values in field_values.items():
        if len(values) == 1 and None in values:
            always_null_fields.add(field_path)
        else:
            sometimes_null_fields.add(field_path)
    
    return {
        'always_null': always_null_fields,
        'sometimes_null': sometimes_null_fields
    }


def _collect_field_info(obj: Any, field_values: Dict[str, Set], path: str):
    """
    Recursively collect field information from nested objects.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            # Convert value to hashable type for set storage
            hashable_value = _make_hashable(value)
            field_values[current_path].add(hashable_value)
            _collect_field_info(value, field_values, current_path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            current_path = f"{path}[{i}]"
            _collect_field_info(item, field_values, current_path)


def _make_hashable(value: Any) -> Any:
    """
    Convert a value to a hashable type for storage in a set.
    """
    if isinstance(value, (list, dict)):
        return str(type(value).__name__)  # Store type name instead of the object
    return value


def remove_null_fields(obj: Any, always_null_fields: Set[str], path: str = "") -> Any:
    """
    Recursively remove fields that are always null from the object.
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            
            # Skip if this field is always null
            if current_path in always_null_fields:
                continue
            
            # Recursively process nested objects
            if isinstance(value, (dict, list)):
                processed_value = remove_null_fields(value, always_null_fields, current_path)
                if processed_value is not None:  # Don't add if it became None
                    result[key] = processed_value
            else:
                result[key] = value
        
        return result if result else None
    
    elif isinstance(obj, list):
        result = []
        for i, item in enumerate(obj):
            current_path = f"{path}[{i}]"
            processed_item = remove_null_fields(item, always_null_fields, current_path)
            if processed_item is not None:
                result.append(processed_item)
        
        return result if result else None
    
    else:
        return obj


def clean_ocsf_files(data_dir: str, output_dir: str = None, dry_run: bool = False):
    """
    Clean OCSF JSON files by removing always-null fields.
    """
    if output_dir is None:
        output_dir = data_dir
    
    if not dry_run and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Analyze null fields
    print("Analyzing null fields...")
    field_analysis = analyze_null_fields(data_dir)
    
    always_null = field_analysis['always_null']
    sometimes_null = field_analysis['sometimes_null']
    
    print(f"\nFound {len(always_null)} fields that are always null:")
    for field in sorted(always_null):
        print(f"  - {field}")
    
    print(f"\nFound {len(sometimes_null)} fields that sometimes have values:")
    for field in sorted(sometimes_null):
        print(f"  - {field}")
    
    if dry_run:
        print("\nDRY RUN: No files will be modified.")
        return
    
    # Process each JSON file
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    print(f"\nProcessing {len(json_files)} files...")
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_dir, filename)
        
        print(f"Cleaning {filename}...")
        
        cleaned_records = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line.strip())
                    cleaned_record = remove_null_fields(record, always_null)
                    
                    if cleaned_record is not None:
                        cleaned_records.append(cleaned_record)
                        
                except json.JSONDecodeError as e:
                    print(f"Warning: JSON decode error in {filename}:{line_num}: {e}")
                    continue
        
        # Write cleaned records
        with open(output_path, 'w', encoding='utf-8') as f:
            for record in cleaned_records:
                f.write(json.dumps(record) + '\n')
        
        print(f"  - Original: {os.path.getsize(file_path)} bytes")
        print(f"  - Cleaned:  {os.path.getsize(output_path)} bytes")
        print(f"  - Records:  {len(cleaned_records)}")
    
    print(f"\nCleaning complete! Files saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Clean OCSF JSON files by removing always-null fields')
    parser.add_argument('data_dir', help='Directory containing OCSF JSON files')
    parser.add_argument('--output-dir', help='Output directory (default: same as input)')
    parser.add_argument('--dry-run', action='store_true', help='Analyze without modifying files')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"Error: Directory '{args.data_dir}' does not exist")
        return 1
    
    clean_ocsf_files(args.data_dir, args.output_dir, args.dry_run)
    return 0


if __name__ == "__main__":
    exit(main()) 