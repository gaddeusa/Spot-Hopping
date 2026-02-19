#!/bin/bash
# Install dependencies
yum update -y
yum install -y python3-pip git

# Install Python requests
pip3 install requests boto3

# Create the Termination Handler Directory
mkdir -p /opt/spot-handler

# Copy the handler script (In real life, sync from S3 or Git)
# For this demo, we assume the script is injected or we write it here inline
# (Ideally, you would `aws s3 cp s3://my-bucket/spot_termination_handler.py /opt/spot-handler/`)

# Create Systemd Service for the Handler
cat <<EOF > /etc/systemd/system/spot-handler.service
[Unit]
Description=Spot Instance Termination Handler
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/spot-handler/spot_termination_handler.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# Start the Service
systemctl enable spot-handler
systemctl start spot-handler
