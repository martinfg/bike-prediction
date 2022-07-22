import psycopg2
import sys
import os

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

    # get data
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM bikes_fake;")
        bikes = cur.fetchall()

    log(f"got {len(bikes)} entries back form db.")
    log(f"Done.", actions=[conn.close])

if __name__ == "__main__":
    main()