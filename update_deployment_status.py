import os
import sys
from pyairtable import Api
from datetime import datetime

def update_latest_deployment(status, commit_sha):
    """Update the most recent deployment record with build status"""
    
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    table_id = os.getenv('AIRTABLE_DEPLOYMENTS_TABLE_ID')
    
    if not all([api_key, base_id, table_id]):
        print("Missing Airtable credentials")
        return False
    
    try:
        api = Api(api_key)
        table = api.table(base_id, table_id)
        
        # Find the record with matching commit SHA
        formula = f"{{Commit SHA}} = '{commit_sha}'"
        records = table.all(formula=formula)
        
        if records:
            # Update the first matching record
            record_id = records[0]['id']
            table.update(record_id, {
                'Build Status': status
            })
            print(f"✓ Updated deployment status to: {status}")
            return True
        else:
            print(f"No record found for commit: {commit_sha}")
            return False
            
    except Exception as e:
        print(f"Error updating Airtable: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python update_airtable_status.py <status> <commit_sha>")
        sys.exit(1)
    
    status = sys.argv[1]  # "Success" or "Failed"
    commit_sha = sys.argv[2]
    
    success = update_latest_deployment(status, commit_sha)
    sys.exit(0 if success else 1)