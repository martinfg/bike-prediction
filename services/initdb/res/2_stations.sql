CREATE TABLE IF NOT EXISTS stations (
  station_id   	INTEGER,
  name			VARCHAR(100),
  latitude		FLOAT			NOT NULL,
  longitude		FLOAT			NOT NULL,
  h3_grid7		VARCHAR(15)		NOT NULL,
  h3_grid8		VARCHAR(15)		NOT NULL,
  h3_grid9		VARCHAR(15)		NOT NULL,
  h3_grid10		VARCHAR(15)		NOT NULL,
  PRIMARY KEY(station_id)
);