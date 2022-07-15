import os
import requests
import json
import logging
import sys
import tempfile

from datetime import datetime
from minio import Minio
from minio.error import S3Error

def main():

    # init logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # call api
    api_route = "https://api.nextbike.net/maps/nextbike-live.json?city=1"
    try:
        response_json = requests.get(api_route).json()
        logging.info("fetched latest data from api.")
    except Exception as e:
        logging.error("API not available. Exiting")
        logging.error(e)
        sys.exit(0)
  
    # write data to temporary file
    temp = tempfile.NamedTemporaryFile(mode="w+")
    json.dump(response_json, temp)
    temp.flush()

    # Create a Minio client
    client = Minio(
        "api.storage.sws.informatik.uni-leipzig.de",
        access_key=os.environ["MINIO_TOKEN"],
        secret_key=os.environ["MINIO_KEY"],
    )

    # check if buckets exists
    exists = client.bucket_exists("group8")
    if not exists:
        logging.error("Bucket could not be found. Exiting.")
        sys.exit(0)

    # create filename from current timestamp
    now = datetime.now()
    filename = now.strftime('%Y_%m_%d_%H_%M_%S') + '.json'

    # upload test data
    logging.info(f"writing data as {filename} to bucket")
    client.fput_object(
        bucket_name="group8",
        object_name=f"bikes/{filename}",
        file_path=temp.name,
    )

    # close tempfile
    temp.close()


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        logging.error("S3 error occurred.")
        logging.error(exc)
