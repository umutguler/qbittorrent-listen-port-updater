#!/bin/sh

echo "Current PATH: $PATH"
echo "Activating virtual environment..."
. /app/venv/bin/activate

echo "Virtual environment activated."

echo "Setting up cron job..."
CRON_SCHEDULE=${CRON_MINUTES:-5}  # Default to every 5 minutes if not set
# Setup Cron job with detailed logging
echo "*/${CRON_SCHEDULE} * * * * PATH=$PATH QBIT_HOST=$QBIT_HOST QBIT_PORT=$QBIT_PORT QBIT_USERNAME=$QBIT_USERNAME QBIT_PASSWORD=$QBIT_PASSWORD VPN_PORT_FILE=$VPN_PORT_FILE /app/venv/bin/python /app/update_qbit_listen_port.py --host $QBIT_HOST --port $QBIT_PORT --username $QBIT_USERNAME --password $QBIT_PASSWORD --vpn-port-file $VPN_PORT_FILE >> /var/log/cron_job.log 2>&1" | crontab -

# Output the current crontab for debugging
crontab -l

echo "Cron job set. Running Python script manually..."
# Run Python script manually for initial check and log output
/app/venv/bin/python /app/update_qbit_listen_port.py --host $QBIT_HOST --port $QBIT_PORT --username $QBIT_USERNAME --password $QBIT_PASSWORD --vpn-port-file $VPN_PORT_FILE >> /var/log/cron_job.log 2>&1
cat /var/log/cron_job.log

echo "Starting cron..."
# Start cron in the foreground to keep the container alive
cron -f
