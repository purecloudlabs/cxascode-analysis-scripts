# Log Chomper

A Python tool for processing and analyzing SDK debug logs. This tool extracts SDK DEBUG REQUEST and RESPONSE entries from log files, matches request-response pairs, calculates response times, and performs statistical analysis.

## Features

- Extract SDK DEBUG REQUEST and RESPONSE entries from terraform log files
- Match request-response pairs by transaction ID
- Calculate response times between requests and responses
- Normalize URLs by replacing GUIDs with placeholders
- Generate statistical analysis of response times by endpoint
- Sort results by request count

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - numpy
  - statistics

### Setup
```bash
pip -r requirements.txt
```

## Usage

### Basic Usage

Run the script with input and output file paths:

```bash
python log_chomper.py input.log API.json
```

Where:
- `input.log` is the path to your log file containing SDK DEBUG entries
- `output.json` is the path where the extracted JSON data will be saved

### Processing Steps

The script performs the following steps:

1. Extracts SDK DEBUG REQUEST and RESPONSE entries from the input log file
2. Saves the extracted entries to the specified output JSON file
3. Matches request-response pairs by transaction ID
4. Calculates response times and normalizes URLs
5. Saves the merged records to a new file with "time" prepended to the original output filename
6. Performs statistical analysis on response times by endpoint
7. Prints the results sorted by request count (highest to lowest)

### Output

The script generates two output files:
- `API.json` - Contains all extracted SDK DEBUG entries
- `timeAPI.json` - Contains merged request-response pairs with response times

The statistical analysis is printed to the console, showing:
- Method + URL
- Count of requests
- Minimum response time
- Maximum response time
- Mean response time
- 50th percentile (median)
- 75th percentile
- 99th percentile

## Data Analysis

After running the script, you can use the generated JSON files for further analysis inside of jupyter notebook.  Please install
pandas matplotlib and seaborn:
