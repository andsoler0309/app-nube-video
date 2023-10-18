FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN mkdir -p /app/videos/uploaded
RUN mkdir -p /app/videos/converted

EXPOSE 5000
