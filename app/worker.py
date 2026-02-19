import boto3
import time
import os
import signal
import sys

# Configuration
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789012/spot-hopping-queue" # REPLACE THIS
REGION = "us-east-1"
STOP_FILE = "/tmp/stop_working"

sqs = boto3.client('sqs', region_name=REGION)

def process_message(msg):
    """Simulate work"""
    print(f"Working on task: {msg['Body']}")
    time.sleep(5) # Simulate processing time
    print("Task done.")

def main():
    print("Worker started. Listening for tasks...")
    
    while True:
        # 1. Check if we should stop
        if os.path.exists(STOP_FILE):
             print("Stop signal received. Finishing gracefully.")
             sys.exit(0)

        # 2. Poll SQS
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10 # Long polling
        )
        
        if 'Messages' in response:
            for message in response['Messages']:
                # Double check stop signal before starting work?
                if os.path.exists(STOP_FILE):
                    print("Stop signal received before starting new task. Exiting.")
                    # Message will become visible again after timeout
                    sys.exit(0)
                    
                process_message(message)
                
                # Delete message only after successful processing
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )

if __name__ == '__main__':
    main()
