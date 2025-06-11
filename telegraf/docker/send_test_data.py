#!/usr/bin/env python3
import json
import requests
import argparse
import time
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('metrics_sender')

def read_json_file(file_path):
    """Read a JSON file and return the data"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def send_data(data, api_url, retry=3):
    """Send data to the API with retry logic"""
    headers = {
        'Content-Type': 'application/json',
    }
    
    for attempt in range(retry):
        try:
            logger.info(f"Sending data to {api_url}...")
            response = requests.post(api_url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Success! Response: {response.json()}")
                return True
            else:
                logger.error(f"Failed with status {response.status_code}: {response.text}")
                if attempt < retry - 1:
                    time.sleep(2)
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            if attempt < retry - 1:
                time.sleep(2)
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Send router metrics data to API')
    parser.add_argument('--file', type=str, help='JSON file to send')
    parser.add_argument('--url', type=str, default='http://router_django:8080/api/metrics/', 
                        help='API endpoint URL')
    parser.add_argument('--retry', type=int, default=3, help='Number of retry attempts')
    args = parser.parse_args()
    
    if not args.file:
        logger.error("No input file specified. Use --file parameter.")
        sys.exit(1)
    
    # Read and send data
    data = read_json_file(args.file)
    if data:
        success = send_data(data, args.url, args.retry)
        if success:
            logger.info("Data sent successfully")
            sys.exit(0)
        else:
            logger.error("Failed to send data after retries")
            sys.exit(1)
    else:
        logger.error("No valid data to send")
        sys.exit(1)

if __name__ == "__main__":
    main()