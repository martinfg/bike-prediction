from pathlib import Path
import json
import h3
import pandas as pd


def load_parsed_data():
    data_directory = Path(__file__).resolve().parents[2] / 'data'
    file_path = data_directory / 'parsed' / 'example.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def create_dataframe(data):
    bikes = data
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
            'bike_id': bike_ids,
            'lat': lats,
            'lon': lons,
            'btype': btype
        }
    )

    return bicycle_data


def add_h3(row):
    h3_precision = 8
    return h3.geo_to_h3(row['lat'], row['lon'], h3_precision)


if __name__ == "__main__":
    raw = load_parsed_data()
    df = create_dataframe(raw)
    df['grid_id'] = df.apply(add_h3, axis=1)
    # print(df.head())
    print(df['grid_id'].nunique())
