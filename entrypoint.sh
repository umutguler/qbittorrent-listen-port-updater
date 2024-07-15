#!/bin/sh

# Print out environment PATH for debugging
echo "Current PATH: $PATH"

# Activate the virtual environment
source /app/venv/bin/activate

# Set the default CRON schedule if none provided
CRON_SCHEDULE=${CRON_MINUTES:-5}  # Default to run every 5 minutes if not set

# Setup Cron job with environment variables and redirect output to a log file
echo "*/${CRON_SCHEDULE} * * * * PATH=$PATH QBIT_HOST=$QBIT_HOST QBIT_PORT=$QBIT_PORT QBIT_USERNAME=$QBIT_USERNAME QBIT_PASSWORD=$QBIT_PASSWORD VPN_PORT_FILE=$VPN_PORT_FILE /app/venv/bin/python /app/update_qbit_listen_port.py --host \$QBIT_HOST --port \$QBIT_PORT --username \$QBIT_USERNAME --password \$QBIT_PASSWORD --vpn-port-file \$VPN_PORT_FILE >> /var/log/cron_job.log 2>&1" | crontab -

# Log current crontab for debugging
crontab -l

# Manually run the Python script once before starting cron
echo "Running Python script manually..."
PATH=$PATH QBIT_HOST=$QBIT_HOST QBIT_PORT=$QBIT_PORT QBIT_USERNAME=$QBIT_USERNAME QBIT_PASSWORD=$QBIT_PASSWORD VPN_PORT_FILE=$VPN_PORT_FILE /app/venv/bin/python /app/update_qbit_listen_port.py --host $QBIT_HOST --port $QBIT_PORT --username $QBIT_USERNAME --password $QBIT_PASSWORD --vpn-port-file $VPN_PORT_FILE >> /var/log/cron_job.log 2>&1

# Start cron in the foreground
cron -f
