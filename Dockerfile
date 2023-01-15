FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN mkdir /code

WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
# install system dependencies
 
RUN apt-get update \
  # && apt-get -y install gcc \
  # && apt-get -y install g++ \
  && apt-get -y install unixodbc \
  # && apt-get -y install unixodbc unixodbc-dev libc-dev libffi-dev libxml2 
  && apt-get clean 

# Add SQL Server ODBC Driver 17 for Ubuntu 18.04
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
#   && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
#   && apt-get update 
  # && apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql17 mssql-tools \
  # && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
  # && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
# clean the install.
RUN apt-get -y clean

COPY . /code