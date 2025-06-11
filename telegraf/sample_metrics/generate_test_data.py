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

def generate_interface_data(name, status="up"):
    """Generate random data for a network interface"""
    input_rate = round(random.uniform(100, 950), 1)
    output_rate = round(random.uniform(80, 850), 1)
    errors = random.randint(0, 5) if random.random() < 0.1 else 0  # 10% chance of errors
    
    return {
        "name": name,
        "status": status,
        "bandwidth": 1000,
        "input_rate": input_rate,
        "output_rate": output_rate,
        "errors": errors
    }

def generate_router_data(router_name, num_interfaces=2):
    """Generate random data for a router"""
    cpu_usage = round(random.uniform(10, 95), 1)
    memory_usage = round(random.uniform(30, 90), 1)
    traffic_mbps = round(random.uniform(50, 500), 1)
    
    # Generate interface data
    interfaces = []
    for i in range(num_interfaces):
        interface_name = f"GigabitEthernet0/{i}"
        interfaces.append(generate_interface_data(interface_name))
    
    # Occasionally add a down interface
    if random.random() < 0.2:  # 20% chance
        interfaces.append(generate_interface_data(f"GigabitEthernet0/{num_interfaces}", status="down"))
    
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

def generate_all_router_data(router_names, output_file):
    """Generate data for all routers and save to file"""
    all_data = []
    
    for router_name in router_names:
        num_interfaces = random.randint(1, 4)
        router_data = generate_router_data(router_name, num_interfaces)
        all_data.append(router_data)
    
    try:
        # Create directory if it doesn't exist
        if output_file != '-':
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to file or stdout
        if output_file == '-':
            # Write to stdout
            print(json.dumps(all_data, indent=2))
        else:
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(all_data, f, indent=2)
            
            logger.info(f"Generated test data for {len(router_names)} routers at {output_file}")
    except Exception as e:
        logger.error(f"Error writing data to {output_file}: {str(e)}")
        
    return all_data

def main():
    parser = argparse.ArgumentParser(description='Generate test router metrics data')
    parser.add_argument('--routers', type=str, nargs='+', default=['Router_Core_01', 'Router_Edge_02', 'Router_Access_03'],
                        help='List of router names')
    parser.add_argument('--output', type=str, default='/tmp/metrics/router_data.json',
                        help='Output file path (use "-" for stdout)')
    parser.add_argument('--print', action='store_true', help='Print the generated data to stdout')
    parser.add_argument('--count', type=int, default=1, help='Number of data sets to generate')
    parser.add_argument('--interval', type=float, default=0, help='Interval between generations in seconds (0 means generate once)')
    parser.add_argument('--no-individual', action='store_true', help='Do not create individual router files')
    args = parser.parse_args()
    
    try:
        iteration = 0
        while True:
            iteration += 1
            if args.count > 0 and iteration > args.count:
                break
            
            logger.info(f"Generating data set #{iteration}")
            
            # Generate data
            data = generate_all_router_data(args.routers, args.output)
            
            # Print if requested
            if args.print:
                print(json.dumps(data, indent=2))
            
            # Also create individual files for each router
            if not args.no_individual and args.output != '-':
                for router_data in data:
                    try:
                        router_name = router_data['router_name']
                        router_file = os.path.join(os.path.dirname(args.output), f"{router_name}.json")
                        with open(router_file, 'w') as f:
                            json.dump(router_data, f, indent=2)
                        logger.debug(f"Created individual file for {router_name} at {router_file}")
                    except Exception as e:
                        logger.error(f"Error creating individual file for {router_name}: {str(e)}")
            
            # If we're not doing intervals or we've reached the count, break
            if args.interval <= 0 or (args.count > 0 and iteration >= args.count):
                break
                
            # Sleep for the specified interval
            logger.info(f"Sleeping for {args.interval} seconds...")
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()