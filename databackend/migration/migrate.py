import os
import sys
import json
import psycopg2
import tempfile
import logging

from minio import Minio
from tqdm import tqdm


def get_chunks(conn, offset=0, chunk_size=100):
    with conn.cursor() as cur:
        sql = """
            SELECT (date + time) as dt, data
            FROM bikes
            ORDER BY dt ASC
            OFFSET %s
            LIMIT %s
            """
        cur.execute(sql, (offset, chunk_size))
        return cur.fetchall()

def main():

    # init logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # create db connection
    try:
        conn = psycopg2.connect("host=localhost dbname=nextbike_api user=s4ki")
        logging.info("connection to database established.")
    except Exception as e:
        logging.error("could not establish connection to database:")
        logging.error(e)
        sys.exit(0)

    # Create a Minio client
    client = Minio(
        "api.storage.sws.informatik.uni-leipzig.de",
        access_key=os.environ["MINIO_TOKEN"],
        secret_key=os.environ["MINIO_KEY"],
    )

    #get total of entries
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM bikes")
        num_entries = cur.fetchone()[0]

    logging.info(f"found {num_entries} entries in database")

    # process data chunk wise
    chunk_size = 10
    current_step = 0
    logging.info(f"chunk size is: {chunk_size}")
    while True:

        logging.info(f"getting next chunk")
        # get entries from db
        entries = get_chunks(conn, offset=current_step+chunk_size, chunk_size=chunk_size)
        logging.info(f"processing entries {current_step + len(entries)} / {num_entries}")
        if len(entries) == 0:
            break
        else:
            current_step += chunk_size


        logging.info("pushing data to bucket")
        for e in tqdm(entries):

            timestamp, json_data = e

            # write data to temporary file
            temp = tempfile.NamedTemporaryFile(mode="w+")
            json.dump(json_data, temp)
            temp.flush()

            # create filename from current timestamp
            filename = timestamp.strftime('%Y_%m_%d') + '/' + timestamp.strftime('%Y_%m_%d_%H_%M_%S') + '.json'

            # push to minio bucket
            client.fput_object(
                bucket_name="group8",
                object_name=f"bikes/{filename}",
                file_path=temp.name,
            )

            # close tempfile
            temp.close()

    conn.close()
    logging.info("Done!")
    
if __name__ == "__main__":
    main()