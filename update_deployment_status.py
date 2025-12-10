#!/usr/bin/env python3
"""
Update Airtable Deployment Status after GitHub Actions completes
"""

import os
import sys
from pyairtable import Api
from datetime import datetime, timedelta

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
        print(f"API Key present: {bool(api_key)}")
        print(f"Base ID present: {bool(base_id)}")
        print(f"Table ID present: {bool(table_id)}")
        return False
    
    try:
        # Initialize Airtable API
        api = Api(api_key)
        table = api.table(base_id, table_id)
        
        # Get recent records (last 10 minutes)
        # We look for the most recent record since Zapier just created it
        all_records = table.all()
        
        if not all_records:
            print("WARNING: No records found in Airtable")
            return False
        
        # Sort by created time (most recent first)
        sorted_records = sorted(
            all_records, 
            key=lambda x: x['createdTime'], 
            reverse=True
        )
        
        # Find record matching commit SHA or use most recent
        target_record = None
        
        # First try to find exact match by Commit SHA
        for record in sorted_records[:5]:  # Check last 5 records
            fields = record['fields']
            record_sha = fields.get('Commit SHA', '')
            
            # Match full SHA or short SHA (first 7 chars)
            if record_sha == commit_sha or record_sha == commit_sha[:7]:
                target_record = record
                print(f"Found record by SHA match: {record['id']}")
                break
        
        # If no SHA match, use the most recent record (likely just created by Zapier)
        if not target_record:
            target_record = sorted_records[0]
            print(f"Using most recent record: {target_record['id']}")
        
        # Update the record with build status
        record_id = target_record['id']
        
        updated_fields = {
            'Build Status': status
        }
        
        table.update(record_id, updated_fields)
        
        print(f"✓ Successfully updated deployment status to: {status}")
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
        print("\nExample:")
        print('  python update_deployment_status.py "Success" "abc123def456"')
        sys.exit(1)
    
    status = sys.argv[1]  # "Success" or "Failed"
    commit_sha = sys.argv[2]
    
    # Validate status
    if status not in ["Success", "Failed"]:
        print(f"ERROR: Invalid status '{status}'. Must be 'Success' or 'Failed'")
        sys.exit(1)
    
    success = update_deployment_status(status, commit_sha)
    
    sys.exit(0 if success else 1)