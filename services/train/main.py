import os
import sys
import psycopg2
import logging
import mlflow

from mlflow.tracking import MlflowClient
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
    precision = 8 # precision (which hexagon grid size to use)
    history = 3 # history range (how many hours in the past are used as features)
    prediction_horizon = 3 # how many timesteps (hours) are predicted into the future
    locations = ["881f1a8cb7fffff", "881f1a8ca7fffff", "881f1a1659fffff"] # list of locations that are covered by models
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
            SELECT date_trunc('hour', time) AS time, h3_grid{precision} as location, COUNT(*) / 12 as free_bikes
            FROM bikes 
            WHERE h3_grid8 = '881f1a8cb7fffff'
            OR h3_grid8 = '881f1a8ca7fffff'
            OR h3_grid8 = '881f1a1659fffff'
            GROUP BY date_trunc('hour', time), location
            ORDER BY time DESC, location DESC
        """)
        cur.execute(query)
        data = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
    log("Database connection closed.", actions=[conn.close])
    
    # init mlflow
    log(f"Experiments will be tracked with mlflow to URI: {mlflow.get_tracking_uri()}")
    experiment = mlflow.set_experiment("group8-baseline")

    with mlflow.start_run(experiment_id=experiment.experiment_id):  

        # build dataset & prepare data
        dataset = Dataset(column_names, data)
        dataset.prepare_samples(history, prediction_horizon)
        mlflow.log_param("num_samples", len(dataset))

        # train and test model
        baseline_model = BaselineModel(locations, prediction_horizon)
        scores = baseline_model.train_and_test(dataset)

        # log model to model registry
        model_name = "group8-baselinemodel"
        client = MlflowClient()

        # log model in registry        
        model_info = mlflow.pyfunc.log_model(
            artifact_path="model",
            python_model=baseline_model,
        )
        model_uri = model_info.model_uri

        # register model
        model_details = mlflow.register_model(
            model_uri=model_uri, 
            name=model_name,
        )   
        model_version = model_details.version # will be assigned automatically 

        # activate model by moving it to production stage
        client.transition_model_version_stage(
            name=model_name,
            version=model_version,
            stage='Production',
        )

        # load model from registry
        model = mlflow.pyfunc.load_model(
            model_uri=f"models:/{model_name}/Production"
        )

        # make prediction with loaded model on test sample

        test_sample = dataset["881f1a8ca7fffff"].dropna().iloc[:10]
        # print("Test sample:")
        # print(test_sample)
        predictions = model.predict(test_sample)
        # print("Predictions:")
        print(predictions)
        # predictions.to_csv("predictions.csv")

        # log scores
        log(scores)
        mae = scores['overall']['mae']
        for idx, _mae in enumerate(mae):            
            mlflow.log_metric(f"mae_t{idx+1}", _mae)

        # make prediction with loaded model for the three locations for the next three hours and save it to the database
        
        # Use the second latest entry because the hour will be complete then
        augustusplatz = dataset["881f1a8cb7fffff"].iloc[[1]]
        clarapark = dataset["881f1a8ca7fffff"].iloc[[1]]
        lenepark = dataset["881f1a1659fffff"].iloc[[1]]

        # print(f"Prediction Augustusplatz: {model.predict(augustusplatz)}")
        # print(f"Prediction Clarapark: {model.predict(clarapark)}")
        # print(f"Prediction Lenepark: {model.predict(lenepark)}")

if __name__ == "__main__":
    main()