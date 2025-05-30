#!/usr/bin/env python3
"""
Log Analyzer - A tool for processing and analyzing SDK debug logs from a terraform log file.

This script processes log files containing SDK DEBUG REQUEST and RESPONSE entries,
extracts JSON data, matches request-response pairs, and performs statistical analysis.
"""

import json
import re
import argparse
import os
import statistics
import numpy as np
from datetime import datetime
from collections import defaultdict

# Regular expression patterns
SDK_DEBUG_PATTERN = r'SDK DEBUG (REQUEST|RESPONSE)'
JSON_EXTRACT_PATTERN = r'(\{.*\})$'
GUID_PATTERN = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'


def process_log_file(input_file, output_file):
    """
    Process a log file to extract SDK DEBUG REQUEST and RESPONSE entries.
    
    Args:
        input_file (str): Path to the input log file
        output_file (str): Path to the output JSON file
    
    Returns:
        bool: True if processing was successful, False otherwise
    """
    parsed_messages = []
    
    try:
        # Read and process the input log file
        with open(input_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                try:
                    parsed_message = _parse_log_line(line)
                    if parsed_message:
                        parsed_messages.append(parsed_message)
                except json.JSONDecodeError as e:
                    print(f"Error parsing log line: {line.strip()}. Error: {e}")
        
        # Write parsed JSON messages to output file
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(parsed_messages, outfile, indent=2)
            
        print(f"Successfully processed {len(parsed_messages)} SDK DEBUG entries to {output_file}")
        return True
        
    except FileNotFoundError:
        print(f"Input file {input_file} not found")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def _parse_log_line(line):
    """
    Parse a single log line to extract SDK DEBUG information.
    
    Args:
        line (str): A single line from the log file
    
    Returns:
        dict: Parsed JSON object or None if no SDK DEBUG data found
    """
    try:
        # Parse the line as JSON
        log_entry = json.loads(line.strip())
        message = log_entry.get('@message', '')
        
        # Check if the message contains SDK DEBUG REQUEST or RESPONSE
        if re.search(SDK_DEBUG_PATTERN, message):
            # Extract the JSON string from the message
            json_str_match = re.search(JSON_EXTRACT_PATTERN, message)
            if json_str_match:
                json_str = json_str_match.group(1)
                # Parse the inner JSON string
                inner_json = json.loads(json_str)
                
                # Add timestamp from the outer record to the inner JSON
                timestamp = log_entry.get('@timestamp')
                if timestamp:
                    inner_json['timestamp'] = timestamp
                return inner_json
    except json.JSONDecodeError as e:
        print(f"Error parsing inner JSON in line: {line.strip()}. Error: {e}")
    
    return None


def merge_request_response(output_file):
    """
    Match SDK DEBUG REQUEST and RESPONSE pairs and calculate response times.
    
    Args:
        output_file (str): Path to the JSON file containing parsed SDK DEBUG entries
    
    Returns:
        str: Path to the output file with merged records, or None if an error occurred
    """
    # Generate the new output file name with "time" prepended
    dir_name = os.path.dirname(output_file)
    base_name = os.path.basename(output_file)
    time_output_file = os.path.join(dir_name, f"time{base_name}")
    
    try:
        # Read the processed JSON data
        records = _read_json_file(output_file)
        if not records:
            return None
        
        # Log unique HTTP methods found
        _log_unique_methods(records, "input")
        
        # Separate and match requests and responses
        requests, responses = _separate_requests_responses(records)
        merged_records = _create_merged_records(requests, responses)
        
        # Write merged records to the new output file
        with open(time_output_file, 'w', encoding='utf-8') as outfile:
            json.dump(merged_records, outfile, indent=2)
            
        print(f"Successfully merged {len(merged_records)} request-response pairs to {time_output_file}")
        return time_output_file
        
    except Exception as e:
        print(f"An error occurred during merge: {e}")
        return None


def _read_json_file(file_path):
    """
    Read and parse a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
    
    Returns:
        list: Parsed JSON data or None if an error occurred
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as infile:
            return json.load(infile)
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {file_path}: {e}")
        return None


def _log_unique_methods(records, stage=""):
    """
    Log unique HTTP methods found in records.
    
    Args:
        records (list): List of record dictionaries
        stage (str): Description of the processing stage
    """
    methods = set()
    for record in records:
        if 'invocation_method' in record:
            methods.add(record['invocation_method'])
    print(f"Found methods in {stage} records: {methods}")


def _separate_requests_responses(records):
    """
    Separate records into requests and responses.
    
    Args:
        records (list): List of record dictionaries
    
    Returns:
        tuple: (requests dict, responses dict) indexed by transaction_id
    """
    requests = {}
    responses = {}
    
    for record in records:
        debug_type = record.get('debug_type')
        transaction_id = record.get('transaction_id')
        
        if debug_type == "SDK DEBUG REQUEST" and transaction_id:
            requests[transaction_id] = record
        elif debug_type == "SDK DEBUG RESPONSE" and transaction_id:
            responses[transaction_id] = record
    
    return requests, responses


def _create_merged_records(requests, responses):
    """
    Create merged records from matching request-response pairs.
    
    Args:
        requests (dict): Request records indexed by transaction_id
        responses (dict): Response records indexed by transaction_id
    
    Returns:
        list: Merged records with calculated response times
    """
    merged_records = []
    
    for transaction_id, request in requests.items():
        if transaction_id in responses:
            response = responses[transaction_id]
            
            # Create a merged record based on the request
            merged_record = request.copy()
            merged_record['debug_type'] = "SDK DEBUG MERGE"
            
            # Process timestamps
            req_timestamp = request.get('timestamp')
            resp_timestamp = response.get('timestamp')
            
            if 'timestamp' in merged_record:
                del merged_record['timestamp']
            
            merged_record['request_timestamp'] = req_timestamp
            merged_record['response_timestamp'] = resp_timestamp
            merged_record['invocation_status_code'] = response.get("invocation_status_code")
            
            # Create normalized URL
            url = merged_record.get('invocation_url', '')
            normalized_url = re.sub(GUID_PATTERN, '{GUID}', url, flags=re.IGNORECASE)
            merged_record['normalized_url'] = normalized_url
            
            # Calculate response time
            merged_record['response_time_ms'] = _calculate_response_time(
                req_timestamp, resp_timestamp, transaction_id)
            
            merged_records.append(merged_record)
    
    return merged_records


def _calculate_response_time(req_timestamp, resp_timestamp, transaction_id):
    """
    Calculate the time difference between request and response.
    
    Args:
        req_timestamp (str): Request timestamp
        resp_timestamp (str): Response timestamp
        transaction_id (str): Transaction ID for error reporting
    
    Returns:
        float: Time difference in milliseconds or None if calculation failed
    """
    try:
        req_time = datetime.fromisoformat(req_timestamp.replace('Z', '+00:00'))
        resp_time = datetime.fromisoformat(resp_timestamp.replace('Z', '+00:00'))
        return (resp_time - req_time).total_seconds() * 1000
    except (ValueError, AttributeError, TypeError) as e:
        print(f"Error calculating time difference for transaction {transaction_id}: {e}")
        return None


def analyze_response_times(time_output_file):
    """
    Analyze response times by method and URL.
    
    Args:
        time_output_file (str): Path to the file with merged request-response records
    
    Returns:
        bool: True if analysis was successful, False otherwise
    """
    try:
        # Read the merged records
        records = _read_json_file(time_output_file)
        if not records:
            return False
        
        # Log unique HTTP methods found
        _log_unique_methods(records, "analysis")
        
        # Group and analyze response times
        grouped_times = _group_response_times(records)
        _print_response_time_statistics(grouped_times)
        
        return True
        
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return False


def _group_response_times(records):
    """
    Group response times by method and URL.
    
    Args:
        records (list): List of merged record dictionaries
    
    Returns:
        dict: Response times grouped by method+URL
    """
    grouped_times = defaultdict(list)
    
    for record in records:
        method = record.get('invocation_method', 'UNKNOWN')
        url = record.get('normalized_url', 'UNKNOWN')
        response_time = record.get('response_time_ms')
        
        if response_time is not None:
            key = f"{method} {url}"
            grouped_times[key].append(response_time)
    
    return grouped_times


def _print_response_time_statistics(grouped_times):
    """
    Print statistics for response times grouped by method and URL.
    
    Args:
        grouped_times (dict): Response times grouped by method+URL
    """
    print("\nResponse Time Statistics (in milliseconds):")
    print("-" * 100)
    print(f"{'Method + URL':<40} {'Count':<8} {'Min':<8} {'Max':<8} {'Mean':<8} {'50%':<8} {'75%':<8} {'99%':<8}")
    print("-" * 100)
    
    # Create a list of (key, times) tuples sorted by count in descending order
    sorted_items = sorted(grouped_times.items(), key=lambda x: len(x[1]), reverse=True)
    
    for key, times in sorted_items:
        if not times:
            continue
            
        count = len(times)
        min_time = min(times)
        max_time = max(times)
        mean_time = statistics.mean(times)
        
        # Calculate percentiles
        p50 = np.percentile(times, 50)
        p75 = np.percentile(times, 75)
        p99 = np.percentile(times, 99)
        
        print(f"{key[:39]:<40} {count:<8d} {min_time:<8.2f} {max_time:<8.2f} {mean_time:<8.2f} "
              f"{p50:<8.2f} {p75:<8.2f} {p99:<8.2f}")


def main():
    """
    Main entry point for the script.
    
    Parses command line arguments and orchestrates the log processing workflow.
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Process log files to extract and analyze SDK DEBUG messages')
    parser.add_argument('input_file', help='Path to the input log file')
    parser.add_argument('output_file', help='Path to the output JSON file')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process the log file with provided arguments
    if process_log_file(args.input_file, args.output_file):
        # Merge request and response records
        time_output_file = merge_request_response(args.output_file)
        
        # Analyze response times
        if time_output_file:
            analyze_response_times(time_output_file)


if __name__ == "__main__":
    main()