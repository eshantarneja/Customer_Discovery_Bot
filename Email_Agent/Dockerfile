FROM python:3.9-slim

WORKDIR /app

# Install git for handling Git-based dependencies
RUN apt-get update && apt-get install -y git

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn==20.1.0

# Copy the application code
COPY . .

ENV PORT=8080

# Increase timeout to 120 seconds to allow for initialization
CMD exec gunicorn --bind :$PORT --timeout 120 api_flask:app