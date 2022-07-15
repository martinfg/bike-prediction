from pathlib import Path
import io
import json
import h3
import pandas as pd
from minio import Minio
from minio.error import InvalidResponseError
import pyjq


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


def load_raw_data():
    # TODO add parameter for date (range)

    # this api is going to change soon to https://api.storage.sws.informatik.uni-leipzig.de/
    client = Minio("api.storage.sws.informatik.uni-leipzig.de",
                   access_key='AmYj3poc3YASEwm1',
                   secret_key='5jGMQRPY6MFAvDnhmPqwrOs6nM54atw7')

    # Get a full object
    try:
        data = client.get_object('group8', '/bikes/2022_07_15_09_33_11.json')
        return json.load(io.BytesIO(data.data))

    except InvalidResponseError as err:
        print(err)


def create_bike_df(raw_data):

    script_directory = Path(__file__).resolve().parents[2] / 'src/data'

    with open(script_directory / "parse_bikes.jq") as f:
        bike_script = f.read()

    bikes = pyjq.first(script = bike_script, value=raw_data)

    bike_ids = []
    lats = []
    lons = []
    btype = []

    for b in bikes:
        bike_ids.append(b['number'])
        lats.append(b['latitude'])
        lons.append(b['longitude'])
        btype.append(b['bike_type'])

    bicycle_data = pd.DataFrame(
        {
            'lat': lats,
            'lon': lons,
            'btype': btype
        },
        index=bike_ids
    )

    bicycle_data.index.name = "bid"

    return bicycle_data


def create_stations_df(raw_data):

    script_directory = Path(__file__).resolve().parents[2] / 'src/data'
    
    with open(script_directory / "parse_stations.jq") as f:
        station_script = f.read()

    stations = pyjq.first(script=station_script, value=raw_data)

    names = []
    numbers = []
    lats = []
    lons = []
    bikes = []
    av_bikes = []
    nav_bikes = []

    for s in stations:
        names.append(s['name'])
        numbers.append(s['number'])
        lats.append(s['latitude'])
        lons.append(s['longitude'])
        bikes.append(s['bikes'])
        av_bikes.append(s['available_bikes'])
        nav_bikes.append(s['booked_bikes'])

    station_data = pd.DataFrame(
        {
            'name': names,
            'lat': lats,
            'lon': lons,
            'bikes': bikes,
            'av_bikes': av_bikes,
            'non_av_bikes': nav_bikes
        },
        index=numbers
    )

    station_data.index.name = "sid"

    return station_data


def add_h3(row, h3_precision):
    return h3.geo_to_h3(row['lat'], row['lon'], h3_precision)


def save_dataframe(df, name):
    # TODO insert the dataframe later to our database, add date information as column
    data_directory = Path(__file__).resolve().parents[2] / 'data' / 'processed'
    df.to_csv(data_directory / name, encoding='utf-8-sig')


if __name__ == "__main__":
    # Here you can specify the H3 resolutions for which you want to have the values in your final dataframe
    h3_resolutions = range(7, 11)

    raw_data = load_raw_data()

    bike_df = create_bike_df(raw_data)
    stations_df = create_stations_df(raw_data)

    for res in h3_resolutions:
        col_name = 'h3_grid_res_' + str(res)
        bike_df[col_name] = bike_df.apply(lambda x: add_h3(x, res), axis=1)
        stations_df[col_name] = stations_df.apply(lambda x: add_h3(x, res), axis=1)

    save_dataframe(bike_df, "single_bikes.csv")
    save_dataframe(stations_df, 'single_stations.csv')

    for res in h3_resolutions:
        col_name = 'h3_grid_res_' + str(res)
        save_dataframe(bike_df.groupby(col_name).size().reset_index(name='counts'),
                       "aggregated_bikes_res_" + str(res) + ".csv")
        save_dataframe(stations_df.groupby(col_name).size().reset_index(name='counts'),
                       "aggregated_stations_res_" + str(res) + ".csv")
