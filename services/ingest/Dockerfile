FROM python:3.9-slim

# define working dir
WORKDIR /app

# install app dependecies
COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# # set environmental variables
# ENV POSTGRES_HOST timescaledb
# ENV POSTGRES_DB bikes
# ENV POSTGRES_USER postgres
# ENV POSTGRES_PASSWORD postgres
# ENV API_URL https://s4ki.uber.space

# copy schemata
COPY ./res/* ./res/

# copy app
COPY ./app.py ./app.py
