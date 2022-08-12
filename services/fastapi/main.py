from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import os
import pandas as pd
import psycopg2
import sys


try:
    from dotenv import load_dotenv
    use_env_file = True
except:
    use_env_file = False

app = FastAPI(root_path="/fastapi", docs_url='/docs', openapi_url='/openapi.json')

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def log(msg, error=None, actions=[]):

    logging.info(msg)
    if error != None: logging.error(error)
    for action in actions: action()


def connect_to_db():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"]
        )
        logging.info("Connection to db successful.")
    except Exception as e:
        log(
            "Connection to DB could not be established. Exiting.", e,
            [lambda: sys.exit(0)]
        )
    return conn


@app.get('/')
def get_root():
  return {'message': 'Welcome to the Bike Prediction API.'}


@app.get("/pvprediction/{grid_id}/")
def get_prior_value_prediction(grid_id: str):

  if use_env_file:
        load_dotenv()

  # connect to database
  conn = connect_to_db()

  # get latest entry from prior value predictions table for corresponding grid id
  with conn.cursor() as cur:
        query = ("""
            SELECT *
            FROM predictions_pv
            WHERE predicting_from = (SELECT MAX(predicting_from) FROM predictions_pv WHERE grid_id=%(gid)s) AND grid_id=%(gid)s
        """)
        cur.execute(query, {'gid': grid_id})
        data = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        log("Database connection closed.", actions=[conn.close])

  df = pd.DataFrame(data=data, columns=column_names)

  # transform the row to json
  result = df.reset_index().to_json(orient='records')

  json_response = json.loads(result)

  return json_response


@app.get("/lrprediction/{grid_id}/")
def get_linear_regression_prediction(grid_id: str):

  if use_env_file:
        load_dotenv()

  # connect to database
  conn = connect_to_db()

  # get latest entry from prior value predictions table for corresponding grid id
  with conn.cursor() as cur:
        query = ("""
            SELECT *
            FROM predictions_lr
            WHERE predicting_from = (SELECT MAX(predicting_from) FROM predictions_lr WHERE grid_id=%(gid)s) AND grid_id=%(gid)s
        """)
        cur.execute(query, {'gid': grid_id})
        data = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        log("Database connection closed.", actions=[conn.close])

  df = pd.DataFrame(data=data, columns=column_names)

  # transform the row to json
  result = df.reset_index().to_json(orient='records')

  json_response = json.loads(result)

  return json_response


# if __name__ == "__main__":
#   print(get_linear_regression_prediction('881f1a8ca7fffff'))