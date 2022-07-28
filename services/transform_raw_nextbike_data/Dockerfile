FROM python:3.9-slim

# define working dir
WORKDIR /app

# set correct timezone within container, install prerequisites for pyjq
RUN apt update && apt install tzdata -y && apt-get install automake autoconf libtool make -y
ENV TZ="Europe/Berlin"

# install app dependecies
COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# copy app
COPY ./app.py ./app.py
COPY ./transform_lib.py ./transform_lib.py
COPY ./parse_bikes.jq ./parse_bikes.jq
COPY ./parse_stations.jq ./parse_stations.jq

# run app
CMD ["python", "app.py"]