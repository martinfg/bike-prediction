FROM python:3.9-slim

# define working dir
WORKDIR /app

# install app dependecies
COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# copy app and libs
COPY ./main.py ./main.py
COPY ./lib/* ./lib/

CMD ["python", "main.py"]