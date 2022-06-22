FROM python:3.8-slim

COPY requirements.txt .
COPY src/ app/

WORKDIR /app/

RUN apt-get update && \
  apt-get install -y make automake gcc g++ git libxml2-dev libxslt-dev python3-lxml && \
  pip install -r ../requirements.txt

ENTRYPOINT [ "python", "app.py" ]
