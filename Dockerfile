FROM python:3.8.3-slim-buster

WORKDIR /project

COPY . .
RUN apt-get update && apt-get install 
RUN pip install -r requirements.txt


ENTRYPOINT "ETL.sh"

