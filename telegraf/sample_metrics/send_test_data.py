#!/usr/bin/env python3
import json
import requests
import argparse
import time
import os
import sys
import logging
from datetime import datetime
from urllib.parse import urljoin

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

def send_data(data, api_url, api_key=None, retry=3):
    """Send data to the API with retry logic"""
    headers = {
        'Content-Type': 'application/json',
    }
    
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    for attempt in range(retry):
        try:
            logger.info(f"Sending data to {api_url}...")
            response = requests.post(api_url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Success! Response: {response.json()}")
                return True
            else:
                logger.error(f"Failed with status {response.status_code}: {response.text}")
                # Wait before retrying
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            if attempt < retry - 1:
                time.sleep(2 ** attempt)
    
    return False

def send_directory(directory, api_url, api_key=None, pattern='*.json'):
    """Send all JSON files in a directory"""
    import glob
    
    success_count = 0
    fail_count = 0
    
    # Get all JSON files in the directory
    file_pattern = os.path.join(directory, pattern)
    files = glob.glob(file_pattern)
    
    logger.info(f"Found {len(files)} files matching pattern {pattern} in {directory}")
    
    for file_path in files:
        logger.info(f"Processing {file_path}...")
        data = read_json_file(file_path)
        
        if data:
            if send_data(data, api_url, api_key):
                success_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1
    
    logger.info(f"Completed sending data. Success: {success_count}, Failed: {fail_count}")
    return success_count, fail_count

def main():
    parser = argparse.ArgumentParser(description='Send router metrics data to API')
    parser.add_argument('--file', type=str, help='JSON file to send')
    parser.add_argument('--dir', type=str, help='Directory containing JSON files to send')
    parser.add_argument('--pattern', type=str, default='*.json', help='File pattern to match in directory')
    parser.add_argument('--url', type=str, default='http://localhost:8080/api/metrics/', 
                        help='API endpoint URL')
    parser.add_argument('--key', type=str, help='API key for authentication')
    parser.add_argument('--generate', action='store_true', 
                        help='Generate test data before sending (requires generate_test_data.py in same directory)')
    parser.add_argument('--interval', type=int, default=0,
                        help='Send data repeatedly at this interval (seconds). 0 means send once.')
    args = parser.parse_args()
    
    # Generate test data if requested
    if args.generate:
        try:
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            generate_script = os.path.join(script_dir, 'generate_test_data.py')
            
            if not os.path.exists(generate_script):
                logger.error(f"Generate script not found at {generate_script}")
                sys.exit(1)
            
            output_dir = args.dir or '/tmp/metrics'
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'generated_data.json')
            
            logger.info(f"Generating test data to {output_file}...")
            os.system(f"python3 {generate_script} --output {output_file}")
            
            # Default to the generated file if no file specified
            if not args.file and not args.dir:
                args.file = output_file
        except Exception as e:
            logger.error(f"Error generating test data: {str(e)}")
            sys.exit(1)
    
    # Validate arguments
    if not (args.file or args.dir):
        logger.error("Either --file or --dir must be specified")
        sys.exit(1)
    
    # Main execution loop
    try:
        while True:
            if args.file:
                logger.info(f"Reading data from file: {args.file}")
                data = read_json_file(args.file)
                if data:
                    send_data(data, args.url, args.key)
            
            if args.dir:
                logger.info(f"Reading data from directory: {args.dir}")
                send_directory(args.dir, args.url, args.key, args.pattern)
            
            # If interval is 0 or not set, exit after one iteration
            if not args.interval:
                break
            
            logger.info(f"Sleeping for {args.interval} seconds before next send...")
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user, exiting...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()