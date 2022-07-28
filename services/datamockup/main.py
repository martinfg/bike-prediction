import os
import sys
import logging
import random
import psycopg2
import h3
from datetime import datetime

def log(msg, error=None, actions=[]):
    logging.info(msg)
    if error != None: logging.error(error)
    for action in actions: action()

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_h3_values(lat, lon, precision_range=(7, 11)):
    return [h3.geo_to_h3(lat, lon, p) for p in range(*precision_range)] 

def get_random_location(lat_bounds=(12.3442, 12.4115), lon_bounds=(51.3295, 51.3531)):
    lon = random.uniform(lon_bounds[0], lon_bounds[1])
    lat = random.uniform(lat_bounds[0], lat_bounds[1])
    return(lon, lat)

def generate_fake_bikes(num):
    bikes = []
    for bike_id in range(num):
        lon, lat = get_random_location() 
        grids = get_h3_values(lat, lon)
        bikes.append((get_timestamp(), bike_id, 0, lon, lat, *grids))
    return bikes

def main():

    # set up logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    # connect to database
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"]
        )
    except Exception as e:
        log(
            "Connection to DB could not be established. Exiting.", e,
            [lambda: sys.exit(0)]
        )

    # insert fake bikes into database
    with conn.cursor() as cur:
        for bike in generate_fake_bikes(num=random.randrange(70, 100)):
            query = "INSERT INTO bikes VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(query, bike) 
    conn.commit()

    # finally close connection
    log(
        f"Done.",
        actions=[conn.close]
    )

if __name__ == "__main__":
    main()