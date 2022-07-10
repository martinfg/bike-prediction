-- DROP TABLE FOR DEBUGGING PURPOSES
-- DROP TABLE bikes_raw;

-- create table for raw 5-minute bike data
CREATE TABLE IF NOT EXISTS bikes_raw (
  time      TIMESTAMPTZ NOT NULL,
  bikes     JSON        NOT NULL
);

-- convert table to hypertable for use with timescaleDB
SELECT create_hypertable('bikes_raw', 'time', if_not_exists => TRUE);