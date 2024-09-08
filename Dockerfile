FROM ubuntu:latest
RUN apt-get update && apt-get install -y ffmpeg
FROM python:3.11
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["bash", "cloud.sh"]
