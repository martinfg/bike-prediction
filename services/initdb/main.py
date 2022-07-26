from doctest import debug
import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

def log(msg, error=None, actions=[]):

    logging.info(msg)
    if error != None: logging.error(error)
    for action in actions: action()

def main():

    # set up logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    # set up database connection as superuser
    try:
        conn = psycopg2.connect(
            user=os.environ["DB_SUPERUSER"],
            password=os.environ["DB_SUPERUSER_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"]
        )
        log("Connection as SUPERUSER established.")
    except Exception as e:
        log(
            "Connection to DB could not be established. Exiting.", e,
            [lambda: sys.exit(0)]
        )

    database=os.environ["DB_NAME"]
    user=os.environ["DB_USER"]
    pw=os.environ["DB_PASSWORD"]

    # create database and add user
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur: 

            # create database
            log("Creating database")
            query = sql.SQL("CREATE DATABASE {database}").format(
                database=sql.Identifier(database)
            )
            cur.execute(query)

            # add user
            log("Adding user.")
            query = sql.SQL("CREATE USER {username} WITH PASSWORD {password}").format(
                username=sql.Identifier(user),
                password=sql.Placeholder()
            )
            cur.execute(query, (pw, ))
            
            # grant access to database
            log("Granting permissions.")
            query = sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {database} TO {username}").format(
                database=sql.Identifier(database),
                username=sql.Identifier(user)
            )
            cur.execute(query)
        
        conn.close()
    except Exception as e:
        log(
            "Error in setting up database and user. Exiting.", e,
            [conn.close, lambda: sys.exit(0)]
        )


    # connect to newly created database
    try:
        conn = psycopg2.connect(
            dbname=database,
            user=user,
            password=pw,
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"]
        )
    except Exception as e:
        log(
            "Connection to DB could not be established. Exiting.", e,
            [lambda: sys.exit(0)]
        )

    # populate database by executing predefined database schemata
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

        
    # finally close connection
    log(
        f"Done.",
        actions=[conn.close]
    )

if __name__ == "__main__":
    main()