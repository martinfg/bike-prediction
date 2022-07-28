import os
import sys
import psycopg2
import logging

from lib.model import BaselineModel
from lib.data import Dataset

try:
    from dotenv import load_dotenv
    use_env_file = True
except:
    use_env_file = False


def log(msg, error=None, actions=[]):

    logging.info(msg)
    if error != None: logging.error(error)
    for action in actions: action()

def get_database_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        log("Database connection established.")
        return conn
    except Exception as e:
        log(
            "Connection to DB could not be established. Exiting.", e,
            [lambda: sys.exit(0)]
        )

def main():

    # FEATURE INFOS
    precision = 7 # precision (which hexagon grid size to use)
    history = 3 # history range (how many hours in the past are used as features)
    prediction_horizon = 3 # how many timesteps (hours) are predicted into the future
    locations = ["8763b1076ffffff", "8763b1054ffffff", "8763b102bffffff"] # list of locations that are covered by models
    # NOTE: We'll have to define those locations a priori and by doing so define a area we cover with predictions
    # because inferring locations from available data when training models is unstable since in dataset in can occur
    # that a certain location has no free bikes ergo will not have a model assigned

    # check if .env file is available (used for local debugging)
    if use_env_file:
        load_dotenv()

    # set up logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    # connect to database
    conn = get_database_connection()    

    # get data (bike count aggregated over 1h and hexagon with given precision)
    with conn.cursor() as cur:
        query = (f"""
            SELECT date_trunc('hour', time) AS time, h3_grid{precision} as location, COUNT(*) as free_bikes
            FROM bikes 
            GROUP BY date_trunc('hour', time), location
            ORDER BY time DESC, location DESC
        """)
        cur.execute(query)
        data = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
    log("Database connection closed.", actions=[conn.close])
    
    # build dataset & prepare data
    dataset = Dataset(column_names, data)
    dataset.prepare_samples(history, prediction_horizon)

    # train and test model
    baseline_model = BaselineModel(locations)
    scores = baseline_model.train_and_test(dataset)
    print(scores)

if __name__ == "__main__":
    main()