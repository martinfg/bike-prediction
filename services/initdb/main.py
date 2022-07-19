import os
import sys
import psycopg2

def log(msg, error=None, actions=[]):

    print(msg)
    if error != None: print(error)
    for action in actions: action()

def main():

    # set up database connection
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=5432
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

        
    # finally close connection
    log(
        f"Done.",
        actions=[conn.close]
    )

if __name__ == "__main__":
    main()