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

# Increase timeout to 1800 seconds (30 minutes) to match Cloud Run service timeout
CMD exec gunicorn --bind :$PORT --workers 2 --timeout 1800 --keep-alive 5 --log-level debug api_flask:app