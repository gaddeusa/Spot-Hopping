#!/usr/bin/env python3
import time
import requests
import logging
import signal
import os
import subprocess

# Configure Logging

# Configure Logging
def setup_logging():
    log_file = '/var/log/spot-handler.log' if os.name == 'posix' else 'spot-handler.log'
    try:
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO,
            filename=log_file
        )
    except Exception:
        # Fallback to console if file access fails
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

METADATA_URL = "http://169.254.169.254/latest/meta-data/spot/instance-action"
TOKEN_URL = "http://169.254.169.254/latest/api/token"
POLL_INTERVAL = 5

def get_token():
    """Retrieve IMDSv2 Token"""
    try:
        headers = {'X-aws-ec2-metadata-token-ttl-seconds': '21600'}
        response = requests.put(TOKEN_URL, headers=headers, timeout=2)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logging.debug(f"Could not retrieve token: {e}")
    return None

def check_for_interruption():
    """Check metadata for interruption notice"""
    headers = {}
    token = get_token()
    if token:
        headers['X-aws-ec2-metadata-token'] = token

    try:
        response = requests.get(METADATA_URL, headers=headers, timeout=2)
        if response.status_code == 200:
            data = response.json()
            logging.warning(f"INTERRUPTION DETECTED: {data}")
            return True
        elif response.status_code == 404:
            # Normal state - no interruption
            return False
    except Exception as e:
        logging.error(f"Error checking metadata: {e}")
    
    return False

def drain_node():
    """Execute graceful shutdown logic"""
    logging.info("Initiating Graceful Shutdown...")
    
    # 1. Signal the worker to stop accepting new tasks
    # Example: Create a file that the worker checks
    with open('/tmp/stop_working', 'w') as f:
        f.write('STOP')
    
    # 2. (Optional) Find the worker PID and send SIGTERM
    # This depends on how you run your worker. For now, we assume file check.
    
    # 3. Wait a moment for cleanup (if needed)
    time.sleep(5)
    
    logging.info("Node drained. Ready for termination.")

def main():
    setup_logging()
    logging.info("Spot Termination Handler Started.")
    while True:
        if check_for_interruption():
            drain_node()
            # We can exit loop or keep logging until actual death
            break
        time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main()
