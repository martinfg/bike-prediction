-- generate new fake data on startup
DROP TABLE IF EXISTS bikes_fake;

-- create table for raw 5-minute bike data
CREATE TABLE IF NOT EXISTS bikes_fake (
  time        TIMESTAMPTZ NOT NULL,
  free_bikes  INTEGER     NOT NULL
);

-- convert table to hypertable for use with timescaleDB
SELECT create_hypertable('bikes_fake', 'time', if_not_exists => TRUE);

-- generate fake data
INSERT INTO bikes_fake
SELECT times, floor(random() * (1000-0+1))::int FROM generate_series
        ( '2022-06-01'::date
        , '2022-07-01'::date
        , '30 minutes'::interval) times;

