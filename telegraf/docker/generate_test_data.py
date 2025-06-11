#!/usr/bin/env python3
import json
import random
import time
import os
import sys
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('data_generator')

def generate_router_data(router_name):
    """Generate random data for a router"""
    cpu_usage = round(random.uniform(10, 95), 1)
    memory_usage = round(random.uniform(30, 90), 1)
    traffic_mbps = round(random.uniform(50, 500), 1)
    
    # Generate interface data
    interfaces = []
    num_interfaces = random.randint(1, 3)
    
    for i in range(num_interfaces):
        interface_name = f"GigabitEthernet0/{i}"
        input_rate = round(random.uniform(100, 950), 1)
        output_rate = round(random.uniform(80, 850), 1)
        errors = random.randint(0, 5) if random.random() < 0.1 else 0  # 10% chance of errors
        
        interfaces.append({
            "name": interface_name,
            "status": "up",
            "bandwidth": 1000,
            "input_rate": input_rate,
            "output_rate": output_rate,
            "errors": errors
        })
    
    return {
        "router_name": router_name,
        "timestamp": str(int(time.time())),
        "router_metrics": {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "traffic_mbps": traffic_mbps,
            "interfaces": interfaces
        }
    }

def main():
    parser = argparse.ArgumentParser(description='Generate test router metrics data')
    parser.add_argument('--routers', type=str, nargs='+', default=['Router1', 'Router2'],
                        help='List of router names')
    parser.add_argument('--output', type=str, default='/tmp/metrics/router_data.json',
                        help='Output file path (use "-" for stdout)')
    parser.add_argument('--count', type=int, default=1, help='Number of data sets to generate')
    args = parser.parse_args()
    
    try:
        all_data = []
        for router_name in args.routers:
            data = generate_router_data(router_name)
            all_data.append(data)
        
        # Write to file or stdout
        if args.output == '-':
            print(json.dumps(all_data, indent=2))
        else:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, 'w') as f:
                json.dump(all_data, f, indent=2)
            logger.info(f"Generated test data for {len(args.routers)} routers at {args.output}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()