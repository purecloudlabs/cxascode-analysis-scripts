import json
import logging
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('config.py'))))
import commonlib.config as cfg


# Set up logging
logging.basicConfig(filename='parse_sdk_errors.log', level=logging.ERROR)

def strip_and_replace_guid(uri):
    """
    Strips GUIDs from a URI and replaces them with {ID} placeholder.
    
    Args:
        uri (str): The URI string containing GUIDs to be replaced
        
    Returns:
        str: The URI with all GUIDs replaced with {ID}
        
    Example:
        >>> strip_and_replace_guid("http://api/123e4567-e89b-12d3-a456-426614174000/resource")
        "http://api/{ID}/resource"
    """
    guid_pattern = r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}'
    sanitized_uri=uri

    # Find all GUIDs in the string
    guids = re.findall(guid_pattern, uri)

    # Replace each GUID with {guid}
    for guid in guids:
      replacement = '{ID}'
      sanitized_uri = re.sub(guid, replacement, uri, flags=re.IGNORECASE)

    return sanitized_uri

def read_json_from_file(file_path):
    """
    Reads and parses JSON records from a file, one record per line.

    Args:
        file_path (str): Path to the JSON file to read

    Returns:
        list: List of dictionaries containing the parsed JSON records

    Raises:
        JSONDecodeError: If a line cannot be parsed as valid JSON (error will be logged)
        
    Example:
        >>> records = read_json_from_file("data.json")
        >>> print(records[0])  
        {'id': 1, 'name': 'test'}
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
    Normalizes a list of log records by extracting and transforming SDK debug messages.
    
    Args:
        records (list): List of dictionaries containing log records to normalize
        
    Returns:
        list: List of normalized records containing only SDK debug messages with transformed fields
        
    The function:
    - Filters for info level SDK debug messages
    - Extracts JSON data from the message
    - Adds timestamp from original record
    - Sanitizes URLs by replacing GUIDs
    - Normalizes retry_after values to integers
    - Writes normalized records to a JSON file
    
    Example:
        >>> records = [{"@level": "info", "@message": "SDK DEBUG {...}", "@timestamp": "2023-01-01"}]
        >>> normalized = normalize_records(records)
        >>> print(normalized[0])
        {'timestamp': '2023-01-01', 'sanitized_url': 'http://api/{ID}/resource', ...}
    """
    normalized_records = []

    for record in records:
        level = record.get("@level")
        msg = record.get("@message")
        timestamp = record.get("@timestamp")
        sdk_debug=False

        if msg.find("SDK DEBUG")!=-1:
            sdk_debug=True

        if level=="info" and sdk_debug==True:
           rawData= msg[20:]
           msgJSON  = json.loads(rawData)
           msgJSON["timestamp"]=timestamp
           msgJSON["sanitized_url"]=strip_and_replace_guid(msgJSON["invocation_url"])

           retry_after = msgJSON.get("invocation_retry_after")
           if retry_after==None:
              msgJSON["invocation_retry_after"]=0
           else:
              msgJSON["invocation_retry_after"]=int(msgJSON["invocation_retry_after"])
           
           normalized_records.append(msgJSON)

    c = cfg.Config()
    with open(c.NORMALIZED_GENESYS_SDK_PATH, "w") as f:
        pretty_json=json.dumps(normalized_records, indent=4)
        f.write(pretty_json)        

    return normalized_records
