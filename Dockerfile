FROM python:3.8.3-slim-buster
ENV PYTHONBUFFERED 1

RUN mkdir project
COPY requirements.txt /project/requirements.txt
WORKDIR /project
RUN apt update
RUN pip install -U pip
RUN apt-get -y install gcc libc-dev gnupg curl 

RUN pip install -r requirements.txt

COPY . ./project/

# Install mssql tools to use bcp in ETL Procedures 
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - 
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list | tee /etc/apt/sources.list.d/msprod.list 
RUN apt-get update 
RUN ACCEPT_EULA=y apt-get -y install mssql-tools unixodbc-dev
ENV PATH $PATH:/opt/mssql-tools/bin 

# ETL Procedures 
ENTRYPOINT ["./project/ETL.sh"] 

