import requests
import psycopg2
import json
import logging
import sys

if __name__ == '__main__':

    # init logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # call api
    api_route = "https://api.nextbike.net/maps/nextbike-live.json?city=1"
    try:
        response_dict = requests.get(api_route).json()
        logging.info("fetched latest data from api.")
    except Exception as e:
        logging.error("could not establish connection to database:")
        logging.error(e)
    data = json.dumps(response_dict)  

    # create db connection
    try:
        conn = psycopg2.connect("host=localhost dbname=nextbike_api user=s4ki")
        logging.info("connection to database established.")
    except Exception as e:
        logging.error("could not establish connection to database:")
        logging.error(e)
        sys.exit(0)
        
    # write data to db
    try:
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT INTO 
                bikes (data) 
            VALUES
                ('{data}')
        ''')
        conn.commit() 
        logging.info("database update complete.")
    except Exception as e:
        logging.error("could not write to database:")
        logging.error(e)
        cursor.close()
        conn.close()
        sys.exit(0)

    # close connection
    cursor.close()
    conn.close()


