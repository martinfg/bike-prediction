from pathlib import Path
import json


def read_raw_data():
    data_directory = Path(__file__).resolve().parents[2] / 'data'
    file_path = data_directory / 'raw' / 'bikes.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    print(read_raw_data())