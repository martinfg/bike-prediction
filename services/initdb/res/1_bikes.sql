CREATE TABLE IF NOT EXISTS bikes (
  bike_id   	INTEGER,
  time      	TIMESTAMPTZ,
  bike_type 	INTEGER,
  latitude		FLOAT			NOT NULL,
  longitude		FLOAT			NOT NULL,
  h3_grid7		VARCHAR(15)		NOT NULL,
  h3_grid8		VARCHAR(15)		NOT NULL,
  h3_grid9		VARCHAR(15)		NOT NULL,
  h3_grid10		VARCHAR(15)		NOT NULL,
  PRIMARY KEY(bike_id, time)
);

SELECT create_hypertable('bikes', 'time', if_not_exists => TRUE);
