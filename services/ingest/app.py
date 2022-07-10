import os
import sys
import requests
import psycopg2
import json
import click

from tqdm import tqdm


def log(msg, error=None, actions=[]):

    print(msg)
    if error != None: print(error)
    for action in actions: action()

@click.command()
@click.option('--debug', '-d', is_flag=True)
def main(debug):

    # retrieve envs
    try:
        api_url = os.environ["API_URL"]
        db_host = os.environ["POSTGRES_HOST"]
        db_port = os.environ["POSTGRES_PORT"]
        db_user = os.environ["POSTGRES_USER"]
        db_pw = os.environ["POSTGRES_PASSWORD"]
        db_name = os.environ["POSTGRES_DB"]
    except KeyError as e:
        log(
            "One ore more ENVs not set properly. Exiting.", e,
            [lambda: sys.exit(0)]
        )

    # set up database connection
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pw,
            host=db_host,
            port=db_port
        )
    except Exception as e:
        log(
            "Connection to DB could not be established. Exiting.", e,
            [lambda: sys.exit(0)]
        )


    # set up database by executing predefined database schemata
    res_dir = "./res"
    schemata = [f"{res_dir}/{f}" for f in os.listdir(res_dir) if f.endswith(".sql")]
    log(f"found {len(schemata)} schema(ta) to execute.")
    try:
        for file in schemata:
            with conn.cursor() as cur:
                cur.execute(open(file, "r").read())
        log(f"Successfully executed {len(schemata)} schema(ta).")
        conn.commit()
    except Exception as e:
        log(
            f"Could not initialize database. Error while parsing: {file}. Exiting.", e,
            [conn.rollback, conn.close, lambda: sys.exit(0)])


    # if in debug mode dont retrieve actual data but only use fake data
    if debug:
        log(
            "No actual data is being received in debug-mode. Exiting.",
            actions=[conn.close, lambda: sys.exit(0)]
        )


    # get latest record in database
    with conn.cursor() as cur:
        sql = """ SELECT CAST(extract(epoch FROM (MAX(time))) AS INTEGER) FROM bikes_raw """
        cur.execute(sql)
        maxtime = cur.fetchone()[0]
        
    
    # get amount of records in database
    with conn.cursor() as cur:
        sql = """ SELECT count(*) FROM bikes_raw """
        cur.execute(sql)
        record_count = cur.fetchone()[0]
        

    # update missing records
    if maxtime == None:
        maxtime = 0 # set to 0 so all records will be fetched
    log(f"Most recent record is: {maxtime}.")


    # get latest data from api
    log("Fetching latest data from server.")
    result = []

    # get inital rows to determine size of data to be loaded
    limit = 5 # get data in batches of 5 NOTE: This is not yet properly implemented at the API and defaults to 5
    url = api_url + f'/bikes/{maxtime}?limit={limit}'
    try:
        resp = requests.get(url=url)
        data = resp.json()
        if data["remaining"] == 0:
            log(
                f"No new data available. Local database up to date.",
                actions=[conn.close, lambda: sys.exit(0)]
            )
        result += data["rows"]

        # print({i:data[i] for i in data if i!="rows"})

    except Exception as e:
        log(
            "API is not availabe. Cant fetch latest data. Exiting.", e,
            [conn.close, lambda: sys.exit(0)]
        )

    # get rest of data
    with tqdm(total=data["remaining"]) as pbar:
        next_page = data["next"]
        while True:

            # write to DB batch wise
            # TODO: maybe make this a thread
            for row in result:
                with conn.cursor() as cur:
                    sql = """ INSERT INTO bikes_raw (time, bikes) VALUES(%s, %s) """
                    values = (row["time"], json.dumps(row["bikes"]))
                    cur.execute(sql, values)
            conn.commit()
            result = []

            # get next batch of data from api
            url = api_url + next_page
            resp = requests.get(url=url)
            data = resp.json()
            result += (data["rows"])
            
            # update progress bar
            pbar.update(limit)
            print(pbar)

            # only continue if api has more data to offer
            if data["next"] != "":
                next_page = data["next"]
            else:
                break
    

    with conn.cursor() as cur:
        sql = """ SELECT count(*) FROM bikes_raw """
        cur.execute(sql)
        new_record_count = cur.fetchone()[0]
        
    # finally close connection
    log(
        f"Successfully fetched {new_record_count - record_count} rows from api and wrote to database.",
        actions=[conn.close]
    )

if __name__ == "__main__":
    main()