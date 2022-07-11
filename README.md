## Voraussage von Verfügbarkeit von Leih-Fahrrädern

The aim of this project is to predict availability of rental bikes (nextbike) in Leipzig for a defined are and a given time period into the feature based on availability of the last x hours as well as external factors like weather, day of the week and time of the day. 

## Development

Defaults for all environmental values are stored in the `.env` file, so in order for local deployment no values need to be set. When running the containers, a **timescaleDB** as well as a **Grafana** Container will be spun up. Also a **data ingestion service** will place fake data in the database which can be visualized via Grafana in the browser, which is located at `localhost:3000`. In order to access and manipulate the dashboards, login credentials need to be provided, which default to `admin:admin`.

### Deploy via docker-compose

Run `docker-compose build && docker-compose up` for deploying the containers locally. Ingestion will run once, then exit. 