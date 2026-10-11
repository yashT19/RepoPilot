FROM python:3.10-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p storage

EXPOSE 8000

FROM python:3.10-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get-install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt
RUN pip install --no-chache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p storage

EXPOSE 8000

CMD ["uvicorn","app.main","--host", "0.0.0.0", "--port", "8000"]