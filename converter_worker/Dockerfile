FROM python:3.9-slim

WORKDIR /app

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]

