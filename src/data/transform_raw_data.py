from pathlib import Path
import io
import json
import h3
import pandas as pd
from minio import Minio
from minio.error import InvalidResponseError
import pyjq
from datetime import datetime

import psycopg2


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


def load_raw_data(timestamp):
    # TODO add parameter for date (range)
	# TODO get API adress, access key and secret key from Kubernetes Secret

    bucket_name = 'group8'

    # this api is going to change soon
    client = Minio("api.storage.sws.informatik.uni-leipzig.de",
                   access_key='AmYj3poc3YASEwm1',
                   secret_key='5jGMQRPY6MFAvDnhmPqwrOs6nM54atw7')

    # Get a full object
    try:
        data = client.get_object(bucket_name, obj_name)
        print(data)
        return json.load(io.BytesIO(data.data))

    except InvalidResponseError as err:
        print(err)


def create_bike_df(raw_data):

    script_directory = Path(__file__).resolve().parents[2] / 'src/data'
	script_name = 'parse_bikes.jq'

    with open(script_directory / script_name) as f:
        bike_script = f.read()

    bikes = pyjq.first(script = bike_script, value=raw_data)

    bike_data = pd.DataFrame.from_dict(bikes)
    bike_data = bike_data.set_index('bike_id')

    return bike_data


def create_stations_df(raw_data):

    script_directory = Path(__file__).resolve().parents[2] / 'src/data'
	script_name = 'parse_stations.jq'
    
    with open(script_directory / script_name) as f:
        station_script = f.read()

    stations = pyjq.first(script=station_script, value=raw_data)

    station_data = pd.DataFrame.from_dict(stations)
    station_data = station_data.set_index('station_id')

    return station_data


def add_h3(row, h3_precision):
	# TODO add error handling
	
	h3_grid_id = h3.geo_to_h3(row['latitude'], row['longitude'], h3_precision)
	
    return h3_grid_id


def save_dataframe(df, name):
    # TODO insert the dataframe later to our database, add date information as column
	# TODO check whether record already exists, if yes, abort
    data_directory = Path(__file__).resolve().parents[2] / 'data' / 'processed'
    df.to_csv(data_directory / name, encoding='utf-8-sig')
	
	
def main():
	# TODO add parameter for date range, always take 0, 5, 10 ... 55 as minutes
	# OR check current timestamp, look up what the latest record in the table is (if empty start with first date
	# when we started scraping) and get closest time with 0, 5, 10...55 minutes to current timestamp
	
	# TODO check whether bikes info already in database, if yes skip this data
	
	latest_record = connection to database, min(timestamp)

    first_day = min(datetime(2022, 7, 19), latest_record)
	
	last_day = datetime.now()
	
	date_range = daterange(first_day, last_day)
	
    
    # Here you can specify the H3 resolutions for which you want to have the values in your final dataframe
    h3_resolutions = range(7, 11)
	
	# for day in date_range:
	
		# check if data for this day was already inserted in the db, if not start with time 00 00 00
		# make db query, max time for this day, then add 5 min on top
		
		
		# time = str(timestamp.hour).rjust(2, '0') + "_" + str(timestamp.minute).rjust(2, '0')
		# print(time)
		
		date = str(timestamp.year) + "_" + str(timestamp.month).rjust(2, '0') + "_" + str(timestamp.day).rjust(2, '0')
		
		print(date)
		
		
		prefix_directory = '/bikes/' + date + '/'
		# prefix = '/bikes/' + date + '/' + date + '_' + time
        print(f"Prefix directory: {prefix_directory}")
		
		objects = client.list_objects(bucket_name, prefix)
		
		# if objects = empty: Error message. "The file for the specified datetime could not be found."
        # else if objects iterator contains more than 1 object
        for obj in objects:
            obj_name = obj.object_name.encode('utf-8')
			print(obj_name)
			
			raw_data = load_raw_data(obj_name)
			bike_df = create_bike_df(raw_data)
			stations_df = create_stations_df(raw_data)
			
			for res in h3_resolutions:
				col_name = 'h3_grid_' + str(res)
			    bike_df[col_name] = bike_df.apply(lambda x: add_h3(x, res), axis=1)
			    stations_df[col_name] = stations_df.apply(lambda x: add_h3(x, res), axis=1)
			
			save_dataframe(bike_df, "bikes.csv")
			save_dataframe(stations_df, 'stations.csv')


if __name__ == "__main__":
	main()
	