FROM python:3.9-slim

WORKDIR /app

# Install git for handling Git-based dependencies
RUN apt-get update && apt-get install -y git

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn==20.1.0

COPY . .

ENV PORT=8080

CMD exec gunicorn --bind :$PORT api_flask:app