# dockerfile that runs python and installs the required packages

FROM python:3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update && apt-get upgrade -y \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python", "./main.py"]