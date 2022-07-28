CREATE TABLE IF NOT EXISTS bikes (
  predicting_from      	TIMESTAMPTZ,
  predicting_for      	TIMESTAMPTZ,
  hours_ahead           INTEGER,
  grid_id               VARCHAR(15),
  free_bikes            INTEGER,
  PRIMARY KEY(predicting_from, hours_ahead, grid_id)
);
