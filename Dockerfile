FROM python:3.14-alpine

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY update_qbit_listen_port.py .

USER nobody
HEALTHCHECK --interval=1m --timeout=5s --retries=3 CMD ["test", "-f", "/tmp/healthy"]
ENTRYPOINT ["python", "/app/update_qbit_listen_port.py"]
