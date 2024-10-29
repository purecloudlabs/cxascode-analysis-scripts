import json
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('config.py'))))
import commonlib.config as cfg


# Set up logging
logging.basicConfig(filename='parse_errors.log', level=logging.ERROR)


def read_json_from_file(file_path):
    """
    Reads and parses JSON records from a file, one record per line.
    
    Args:
        file_path (str): Path to the JSON file to read
        
    Returns:
        list: List of parsed JSON records as dictionaries
        
    Raises:
        JSONDecodeError: If a line contains invalid JSON. Error is logged but not raised.
        
    Each line in the file should contain a complete, valid JSON object. Invalid JSON
    lines are logged as errors and skipped.
    """
    records = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                # Attempt to parse each record into a dictionary
                record = json.loads(line)
                
                # Perform any additional processing on the parsed record here...
                # For example, you might extract specific fields or values from the record
                records.append(record)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse line '{line.strip()}' at line {e.lineno}: {e}")
    return records

def normalize_records(records):
    """
    Normalizes Terraform log records into a standardized format.
    
    Args:
        records (list): List of raw Terraform log records to normalize
        
    Returns:
        list: List of normalized records with consistent fields
        
    Each normalized record contains:
        - resource_id: ID of the resource (defaults to "None")
        - timestamp: Timestamp from original record
        - type: Record type (e.g. refresh_start, refresh_complete)
        - module: Terraform module name
        - resource: Resource identifier
        - resource_type: Type of Terraform resource
        - resource_name: Name of the resource
        - action: Action being performed (defaults to "None")
        
    The function handles two types of records:
    1. Records with a "hook" field - typically refresh operations
    2. Records with a "change" field - resource modifications
    
    The normalized records are also written to a JSON file at:
    """
    normalized_records = []


    for record in records:
        #print(record)
        hook = record.get("hook")
        if hook!=None:
            resource_id = "None"
            module = hook["resource"]["module"]
            resource = hook["resource"]["resource"]
            resource_name = hook["resource"]["resource_name"] 
            resource_type =  hook["resource"]["resource_type"]

            if record['type']=="refresh_start" or record['type']=="refresh_complete":
                id=hook["id_value"]

            action="None"

        change = record.get("change")
        if change!=None:
            resource_id = "None"
            module = change["resource"]["module"]
            resource = change["resource"]["resource"] 
            resource_name = change["resource"]["resource_name"] 
            resource_type = change["resource"]["resource_type"]  
            action =   change["action"]

        parsed_record={
            'resource_id': resource_id,
            'timestamp': record['@timestamp'],
            'type':    record['type'],
            'module':  module,
            'resource': resource,
            'resource_type': resource_type,
            'resource_name': resource_name,
            'action': action
        }

    
        normalized_records.append(parsed_record)

    c = cfg.Config()
    with open(c.NORMALIZED_TERRAFORM_LOG_PATH,"w") as f:
        pretty_json=json.dumps(normalized_records, indent=4)
        f.write(pretty_json)

    return normalized_records
