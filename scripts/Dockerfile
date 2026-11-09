FROM python:3.11-slim
WORKDIR /migration
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY migrate_legacy_data.py .
ENTRYPOINT ["python", "migrate_legacy_data.py"]
