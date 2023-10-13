FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN mkdir -p /app/videos/uploaded
RUN mkdir -p /app/videos/converted

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
