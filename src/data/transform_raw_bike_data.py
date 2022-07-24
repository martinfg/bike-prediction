from datetime import datetime, timedelta
import io
import pandas as pd
from pathlib import Path
import pyjq

from transform_lib import list_data, load_raw_data, add_h3, save_dataframe, create_minio_client


def create_bike_df(raw_data, timestamp):

    script_directory = Path(__file__).resolve().parents[2] / 'src/data'
    script_name = 'parse_bikes.jq'
    
    with open(script_directory / script_name) as f:
        bike_script = f.read()

    bikes = pyjq.first(script = bike_script, value=raw_data)

    bike_data = pd.DataFrame.from_dict(bikes)
    bike_data = bike_data.set_index('bike_id')
    bike_data['timestamp'] = timestamp

    return bike_data
	
	
def main():
    bucket_name = "group8"
    client = create_minio_client()

    # Here you can specify the H3 resolutions you want to have as values in your final dataframe
    h3_resolutions = range(7, 11)

    first_date = datetime(2022, 7, 24, 8, 0) # TODO connect to database, get latest date, if empty set date to 2022-6-20
    last_date = datetime(2022, 7, 24, 8, 20) # datetime.now()

    assert first_date < last_date, "First date must be older than last date"

    if first_date.date() == last_date.date():
        print(f"Loading nextbike data from {first_date}.")
    else:
        print(f"Loading nextbike data from {first_date} to {last_date}.")
    
    date_range = pd.date_range(start=first_date, end=last_date)
    
    for date in date_range:
        # create a string out of the date in order to access the data's path of that date
        prefix = str(date.year) + "_" + str(date.month).rjust(2, '0') + "_" + str(date.day).rjust(2, '0')
        directory = "bikes/" + prefix

        obj_to_read = list_data(directory, client, bucket_name)

        if not obj_to_read:
            print("There is no data for this date in MinIO yet.")

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
                bike_df = create_bike_df(raw_data, dt_object)

                for res in h3_resolutions:
                    col_name = 'h3_grid_' + str(res)
                    bike_df[col_name] = bike_df.apply(lambda x: add_h3(x, res), axis=1)
                
                # TODO write to database instead of local
                save_dataframe(bike_df, dt_string + ".csv")


if __name__ == "__main__":
	main()
	