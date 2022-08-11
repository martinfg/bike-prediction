CREATE TABLE IF NOT EXISTS predictions_pv (
  predicting_from      	TIMESTAMPTZ,
  predicting_for      	TIMESTAMPTZ,
  hours_ahead           INTEGER,
  grid_id               VARCHAR(15),
  free_bikes            INTEGER,
  PRIMARY KEY(predicting_from, hours_ahead, grid_id)
);

SELECT create_hypertable('predictions_pv', 'predicting_from', if_not_exists => TRUE);
