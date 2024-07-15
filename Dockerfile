FROM python:3.9-slim

# Install cron, python3-venv, and necessary utilities
RUN apt-get update && \
    apt-get install -y cron python3-venv curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Create a virtual environment
RUN python3 -m venv /app/venv

# Activate the virtual environment and install any needed packages specified in requirements.txt
RUN /app/venv/bin/python -m pip install --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy and set permissions for the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Ensure that the entrypoint uses the virtual environment
ENTRYPOINT ["/app/entrypoint.sh"]

# Start the container with /bin/sh to keep it running for cron jobs
CMD ["/bin/sh", "-c", "cron && tail -f /var/log/cron_job.log"]
