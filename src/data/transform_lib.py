import h3
import io
import json
from minio import Minio
from minio.error import InvalidResponseError
import pandas as pd
from pathlib import Path
import psycopg2


def create_minio_client():
    # TODO get API adress, access key and secret key from Kubernetes Secret
    client = Minio("api.storage.sws.informatik.uni-leipzig.de",
                   access_key='AmYj3poc3YASEwm1',
                   secret_key='5jGMQRPY6MFAvDnhmPqwrOs6nM54atw7')
    return client


def list_data(directory, client, bucket_name):

    try:
        objects = client.list_objects(bucket_name, prefix=directory, recursive=True)

    except InvalidResponseError as err:
        print(err)

    obj_names = []

    for obj in objects:
        obj_names.append(obj.object_name)

    return obj_names


def load_parsed_data():
    # This function is used to test things locally without MinIO
    data_directory = Path(__file__).resolve().parents[2] / 'data'
    bikes_file_path = data_directory / 'parsed' / 'bikes_example.json'
    stations_file_path = data_directory / 'parsed' / 'stations_example.json'
    with open(bikes_file_path, 'r') as f:
        parsed_bike_data = json.load(f)
    with open(stations_file_path, 'r') as f:
        parsed_stations_data = json.load(f)

    return parsed_bike_data, parsed_stations_data


def load_raw_data(obj_name, client, bucket_name):
    try:
        data = client.get_object(bucket_name, obj_name)
        print(data)
        return json.load(io.BytesIO(data.data))

    except InvalidResponseError as err:
        print(err)


def add_h3(row, h3_precision):
	# TODO add error handling
	h3_grid_id = h3.geo_to_h3(row['latitude'], row['longitude'], h3_precision)
	return h3_grid_id


def save_dataframe(df, name):
    # TODO write to database instead of local
    data_directory = Path(__file__).resolve().parents[2] / 'data' / 'processed'
    df.to_csv(data_directory / name, encoding='utf-8-sig')
