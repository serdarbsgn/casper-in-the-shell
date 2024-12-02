FROM python:3.10.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install mysqlclient
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

ENV FLASK_APP=app/webapp.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
