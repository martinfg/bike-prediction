from datetime import datetime
import h3
import io
import json
import logging
from minio import Minio
from minio.error import InvalidResponseError
import os
import pandas as pd
from pathlib import Path
import psycopg2
import sys


def log(msg, error=None, actions=[]):

    logging.info(msg)
    if error != None: logging.error(error)
    for action in actions: action()


def create_minio_client():
    client = Minio(
        "api.storage.sws.informatik.uni-leipzig.de",
        access_key=os.environ["MINIO_TOKEN"],
        secret_key=os.environ["MINIO_KEY"],
    )
    logging.info("connection to bucket established.")

    return client


def list_data(directory, client, bucket_name):

    try:
        objects = client.list_objects(bucket_name, prefix=directory, recursive=True)
        obj_names = []

        for obj in objects:
            obj_names.append(obj.object_name)
        
        return obj_names

    except InvalidResponseError as err:
        log(f"An error occured while listing the data of this directory {directory}", err, [])
        return None

    

def load_raw_data(obj_name, client, bucket_name):
    try:
        data = client.get_object(bucket_name, obj_name)
        print(data)
        return json.load(io.BytesIO(data.data))

    except InvalidResponseError as err:
        log(f"An error occured while reading this object {obj_name}", err, [])


def add_h3(row, h3_precision):
    try:
	    h3_grid_id = h3.geo_to_h3(row['latitude'], row['longitude'], h3_precision)
    except Exception as e:
        log("An error occured while converting the geo location to an H3 grid id. Filling with 0.", e, [])
        h3_grid_id = 0
    
    return h3_grid_id
    
	
def save_dataframe(df, name):
    data_directory = Path(__file__).resolve().parents[1] / 'data'
    df.to_csv(data_directory / name, encoding='utf-8-sig')


def connect_to_db():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"]
            # the following variables can be set for local development in minikube
            # dbname=os.environ["DB_NAME"],
            # user="group8",
            # password=os.environ["DB_PASSWORD"],
            # host='192.168.49.2',
            # port='32259'
        )
        logging.info("Connection to db successful.")
    except Exception as e:
        log(
            "Connection to DB could not be established. Exiting.", e,
            [lambda: sys.exit(0)]
        )
    return conn


def get_latest_db_date(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(time) FROM bikes;")
        latest_db_date = cursor.fetchone()

        if latest_db_date[0] is None:
            return datetime(2022, 6, 20, 22, 10)
        
        else:
            return latest_db_date[0].replace(tzinfo=None)

    except Exception as e:
        log("An error occured while querying the latest date from bike table", e)


def stations_table_empty(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM stations;")
        stations_content = cursor.fetchall()
        if stations_content:
            return False
        else:
            return True

    except Exception as e:
        log("An error occured while querying the stations table", e)


def write_to_table(conn, df, table, index, dt_string):
    """
    Here we are going save the dataframe on disk as 
    a csv file, load the csv file  
    and use copy_from() to copy it to the table
    """
    # Save the dataframe to disk
    tmp_df = "./tmp_dataframe.csv"
    df.to_csv(tmp_df, index_label=index, header=False)
    f = open(tmp_df, 'r')
    cursor = conn.cursor()
    try:
        cursor.copy_from(f, table, sep=",")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        os.remove(tmp_df)
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    logging.info(f"Writing to {table} for {dt_string} was successful.")
    cursor.close()
    os.remove(tmp_df)
    return f
