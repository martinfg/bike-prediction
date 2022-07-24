from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import pyjq

from transform_lib import load_raw_data, add_h3, save_dataframe, create_minio_client


def create_stations_df(raw_data):

    script_directory = Path(__file__).resolve().parents[2] / 'src/data'
    script_name = 'parse_stations.jq'
    
    with open(script_directory / script_name) as f:
        station_script = f.read()

    stations = pyjq.first(script=station_script, value=raw_data)

    station_data = pd.DataFrame.from_dict(stations)
    station_data = station_data.set_index('station_id')

    return station_data
	
	
def main():
    bucket_name = "group8"
    client = create_minio_client()

    # Here you can specify the H3 resolutions you want to have as values in your final dataframe
    h3_resolutions = range(7, 11)

    # The snapshot of that day will be the basis for the station overview
    file_name = "bikes/2022_06_20/2022_06_20_22_10_03.json"

    raw_data = load_raw_data(file_name, client, bucket_name)
    station_df = create_stations_df(raw_data)

    for res in h3_resolutions:
        col_name = 'h3_grid_' + str(res)
        station_df[col_name] = station_df.apply(lambda x: add_h3(x, res), axis=1)
            
    # TODO write to database instead of local
    save_dataframe(station_df, "stations.csv")


if __name__ == "__main__":
	main()
