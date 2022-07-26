CREATE TABLE IF NOT EXISTS bikes (
  time      	TIMESTAMPTZ,
  bike_id   	INTEGER,
  bike_type 	INTEGER,
  longitude		FLOAT			NOT NULL,
  latitude		FLOAT			NOT NULL,
  h3_grid7		VARCHAR(15)		NOT NULL,
  h3_grid8		VARCHAR(15)		NOT NULL,
  h3_grid9		VARCHAR(15)		NOT NULL,
  h3_grid10		VARCHAR(15)		NOT NULL,
  PRIMARY KEY(bike_id, time)
);

SELECT create_hypertable('bikes', 'time', if_not_exists => TRUE);
