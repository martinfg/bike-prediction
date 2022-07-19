## Deploy

deploy via 
```
helm install timescaledb -f myvalues.yaml -f credentials.yaml timescale/timescaledb-single
```

and upgrade via
```
helm upgrade -f myvalues.yaml timescale/timescaledb-single
```
