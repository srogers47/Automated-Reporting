FROM python:3.8.3-slim-buster
# For apt install. Containers are run as non root by default 
USER root 
WORKDIR /project

COPY . ./project
COPY /opt/mssql-tools/bin/sqlcmd ./project 
RUN apt-get update 
RUN pip install -r requirements.txt

# ETL Procedures 
ENTRYPOINT "ETL.sh"  

