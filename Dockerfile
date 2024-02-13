# dockerfile that runs python and installs the required packages

FROM python:3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get upgrade

COPY . .

# VOLUME /file/from/host /path/in/container

CMD [ "python", "./main.py" ]