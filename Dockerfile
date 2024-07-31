FROM python:3.11
WORKDIR /app
COPY . /app
RUN ls
CMD ["bash", "cloud.sh"]
