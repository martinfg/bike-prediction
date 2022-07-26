FROM python:3.9-slim

# define working dir
WORKDIR /app

# set correct timezone within container
RUN apt update && apt install tzdata -y
ENV TZ="Europe/Berlin"

# install app dependecies
COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# copy app
COPY ./app.py ./app.py

# run app
CMD ["python", "app.py"]