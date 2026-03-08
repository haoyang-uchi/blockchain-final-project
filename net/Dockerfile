FROM python:3
RUN apt-get update -y
COPY ./ ./nodes/
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade google-api-python-client
# Following can be commented back in for debugging purposes in interactive (-it) mode
# RUN apt install -y vim