#!/usr/bin/env python3
"""
Update Airtable Deployment Status after GitHub Actions completes
"""

import os
import sys
import time
from pyairtable import Api
from datetime import datetime

def find_deployment_record(table, commit_sha, max_attempts=6, wait_seconds=10):
    """
    Find the deployment record, with retries to wait for Zapier
    
    Args:
        table: Airtable table object
        commit_sha: Commit SHA to match
        max_attempts: Number of retry attempts
        wait_seconds: Seconds to wait between attempts
    """
    
    short_sha = commit_sha[:7]
    
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts}: Looking for commit {short_sha}...")
        
        # Get all records
        all_records = table.all()
        
        if not all_records:
            print("  No records found")
            if attempt < max_attempts:
                print(f"  Waiting {wait_seconds} seconds for Zapier...")
                time.sleep(wait_seconds)
                continue
            return None
        
        # Sort by created time (most recent first)
        sorted_records = sorted(
            all_records,
            key=lambda x: x['createdTime'],
            reverse=True
        )
        
        # Look for matching SHA in recent records
        for record in sorted_records[:10]:  # Check last 10 records
            fields = record['fields']
            record_sha = fields.get('Commit SHA', '')
            
            # Match full SHA or short SHA
            if record_sha == commit_sha or record_sha == short_sha or commit_sha.startswith(record_sha):
                print(f"  Found matching record: {record['id']}")
                print(f"  Commit SHA in Airtable: {record_sha}")
                return record
        
        # No match found, wait and retry
        if attempt < max_attempts:
            print(f"  No matching record found yet")
            print(f"  Most recent commit SHA in Airtable: {sorted_records[0]['fields'].get('Commit SHA', 'none')}")
            print(f"  Waiting {wait_seconds} seconds for Zapier...")
            time.sleep(wait_seconds)
    
    print("WARNING: Could not find matching record after all attempts")
    return None


def update_deployment_status(status, commit_sha):
    """
    Update the deployment record in Airtable with build status
    
    Args:
        status: "Success" or "Failed"
        commit_sha: The commit SHA to find the record
    """
    
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    table_id = os.getenv('AIRTABLE_DEPLOYMENTS_TABLE_ID')
    
    if not all([api_key, base_id, table_id]):
        print("ERROR: Missing Airtable credentials")
        return False
    
    try:
        # Initialize Airtable API
        api = Api(api_key)
        table = api.table(base_id, table_id)
        
        # Find the record with retries
        target_record = find_deployment_record(table, commit_sha)
        
        if not target_record:
            print("ERROR: Could not find deployment record")
            return False
        
        # Update the record
        record_id = target_record['id']
        
        table.update(record_id, {'Build Status': status})
        
        print(f"\n✓ Successfully updated deployment status to: {status}")
        print(f"  Record ID: {record_id}")
        print(f"  Commit SHA: {commit_sha[:7]}")
        
        return True
        
    except Exception as e:
        print(f"ERROR updating Airtable: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python update_deployment_status.py <status> <commit_sha>")
        sys.exit(1)
    
    status = sys.argv[1]
    commit_sha = sys.argv[2]
    
    if status not in ["Success", "Failed"]:
        print(f"ERROR: Invalid status '{status}'")
        sys.exit(1)
    
    success = update_deployment_status(status, commit_sha)
    sys.exit(0 if success else 1)