from datetime import datetime, timedelta
import io
import logging
import pandas as pd
from pathlib import Path
import pyjq

from transform_lib import list_data, load_raw_data, add_h3, create_minio_client, get_latest_db_date, save_dataframe, write_to_table, connect_to_db, log, stations_table_empty


def create_bike_df(raw_data, timestamp):

    script_directory = Path(__file__).resolve().parent
    script_name = 'parse_bikes.jq'
    
    with open(script_directory / script_name) as f:
        bike_script = f.read()

    bikes = pyjq.first(script = bike_script, value=raw_data)

    bike_data = pd.DataFrame.from_dict(bikes)
    bike_data = bike_data.set_index('bike_id')
    bike_data.insert(0, 'time', timestamp)

    return bike_data


def create_stations_df(raw_data):

    script_directory = Path(__file__).resolve().parent
    script_name = 'parse_stations.jq'
    
    with open(script_directory / script_name) as f:
        station_script = f.read()

    stations = pyjq.first(script=station_script, value=raw_data)

    station_data = pd.DataFrame.from_dict(stations)
    station_data = station_data.set_index('station_id')

    return station_data
	
	
def main():
    # set up logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    bucket_name = "group8"
    client = create_minio_client()
    conn = connect_to_db()

    # Here you can specify the H3 resolutions you want to have as values in your final dataframe
    h3_resolutions = range(7, 11)


    # Transformation of raw station data starts here, will only be done once (if stations table is empty)
    if(stations_table_empty(conn)):
        logging.info("The stations table is empty and will now be initialized...")
    
        # The snapshot of that day will be the basis for the station overview
        file_name = "bikes/2022_06_20/2022_06_20_22_10_03.json"

        raw_station_data = load_raw_data(file_name, client, bucket_name)
        station_df = create_stations_df(raw_station_data)

        for res in h3_resolutions:
            col_name = 'h3_grid' + str(res)
            station_df[col_name] = station_df.apply(lambda x: add_h3(x, res), axis=1)

        write_to_table(conn, station_df, 'stations', 'station_id', file_name)


    # Transformation of raw bike data starts here
    first_date = get_latest_db_date(conn)
    logging.info(f"Latest Entry in bikes table is from: {first_date}")
    last_date =  datetime.now()

    assert first_date < last_date, "First date must be older than last date"

    if first_date.date() == last_date.date():
        logging.info(f"Loading nextbike data from {first_date.date()}.")
    else:
        logging.info(f"Loading nextbike data from {first_date.date()} to {last_date.date()}.")
    
    date_range = pd.date_range(start=first_date.date(), end=last_date.date())
    
    for date in date_range:
        # create a string out of the date in order to access the data's path of that date
        prefix = str(date.year) + "_" + str(date.month).rjust(2, '0') + "_" + str(date.day).rjust(2, '0')
        print(prefix)
        directory = "bikes/" + prefix

        obj_to_read = list_data(directory, client, bucket_name)

        if not obj_to_read:
            logging.info(f"There is no data for the date {prefix} in MinIO yet.")

        else:
            # remove obj_names which are <= first_date.time because they are already in the SQL table
            if date.date() == first_date.date():
                time = str(first_date.hour).rjust(2, '0') + "_" + str(first_date.minute).rjust(2, '0')
                file_name_latest_entry = "bikes/" + prefix + "/" + prefix + "_" + time

                # Get the position of the JSON file whose data is already in the SQL table and drop all elements before + itself
                indices = [i for i, s in enumerate(obj_to_read) if file_name_latest_entry in s]

                # if one element is found with the same timestamp then drop the ones before, otherwise don't change the obj_to_read
                if(indices):
                    index = indices[0] + 1
                    obj_to_read = obj_to_read[index:]

            for obj_name in obj_to_read:
                # extract timestamp from filename by splitting it at the slashes and cutting off seconds and .json
                dt_string = obj_name.split("/")[2][:16]
                dt_object = datetime.strptime(dt_string, "%Y_%m_%d_%H_%M")

                raw_data = load_raw_data(obj_name, client, bucket_name)

                try:
                    bike_df = create_bike_df(raw_data, dt_object)
                    for res in h3_resolutions:
                        col_name = 'h3_grid' + str(res)
                        bike_df[col_name] = bike_df.apply(lambda x: add_h3(x, res), axis=1)

                    # save_dataframe(bike_df, dt_string + ".csv")
                    write_to_table(conn, bike_df, 'bikes', 'bike_id', dt_string)

                except Exception as e:
                    log(
                        f"An error occured while transforming and writing this file {obj_name} to the TimescaleDB. Skipping.", e,
                        []
                    )


if __name__ == "__main__":
	main()
	