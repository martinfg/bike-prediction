from fastapi import FastAPI
from typing import Union

import psycopg2
import random

app = FastAPI()
db = None


def query(query_str, params=[]):
    with db.cursor() as cur:
        if len(params) != 0:
            cur.execute(query_str, params)
        else:
            cur.execute(query_str)
        return cur.fetchall()


@app.on_event("startup")
def on_startup() -> None:
    global db 
    db = psycopg2.connect(
            "host=localhost dbname=nextbike_api user=s4ki"
        )


@app.on_event("shutdown")
def on_shutdown():
    db.close()


@app.get("/bikes")
def bikes():
    cnt = query(""" SELECT count(*) from bikes """)
    days = query(""" SELECT (date + time) FROM bikes ORDER BY id ASC """)
    days = [day[0] for day in days]
    return {
        "count": cnt[0][0],
        "earliest": days[0],
        "latest": days[-1] 
    }


@app.get("/bikes/{timestamp}")
def bikes_page(timestamp: int, offset: int = 0, limit: Union[int, None] = 5):
    total = query(""" SELECT COUNT(*) OVER() FROM bikes
            WHERE CAST(extract(epoch FROM (time + date)) AS INTEGER) > %s
            """, (timestamp, ))

    if len(total) == 0: 
        return {
            "prev": "",
            "next": "",
            "remaining": 0,
        } 

    rows = query(
        """ SELECT (date + time), data 
            FROM bikes
            WHERE CAST(extract(epoch FROM (time + date)) AS INTEGER) > %s
            ORDER BY id ASC
            OFFSET %s LIMIT %s; """,
            (timestamp, offset, limit))
    
    remaining = max(0, total[0][0] - offset) 

    data = []
    for row in rows:
        time = row[0]
        try: # some times rows contain no data so will not get appended to response here
            bikes = row[1]["countries"][0]["cities"][0]["places"]
            data.append({"time": time, "bikes": bikes})
        except IndexError as e:
            pass
        except Exception as e:
            pass

    return {
        "prev": f"/bikes/{timestamp}?offset={offset-limit}" if offset != 0 else "",
        "next": f"/bikes/{timestamp}?offset={offset+limit}" if remaining > 0 else "",
        "remaining": remaining,
        "rows": data
    } 
        

@app.get("/randomtimestamp")
def _test():
    rows = query(""" SELECT CAST(extract(epoch FROM (time + date)) AS INTEGER) from bikes """)
    timestamps = [row[0] for row in rows]

    return {
        "randomTimestamp": random.choice(timestamps)
    }
