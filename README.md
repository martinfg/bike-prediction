## Voraussage von Verfügbarkeit von Leih-Fahrrädern

...

### Deployment

**Die Applikation als ganze liegt als Helm Chart (`./bike-prediction`) vor**

Das Helm-Chart enthält einige externe Dependencies (grafana, timescaledb, ...), somit muss vor dem Installieren die Dependency Liste geupdated werden.

```
helm dep update
```

In `./services` sind die einzelnen Komponenten gespeichert, meist Python Skripte mit Dockerfiles. Diese müssen per `docker build` gebaut und dann per `docker push` in die private Docker Registry `group8se4ai` gepushed werden. Die Credentials liegen in den GitLab CI/CD-Settings.

**Installieren des Helm Charts und Deployment auf dem Cluster / Minikube via:**

```
helm install \
--set minio.password=$MINIO_KEY \
--set containerRegistry.dockerconfig=$DOCKER_CONFIG \
--set initdb.credentials.password=$DB_PASSWORD \
bike-prediction ./bike-prediction 
```
Die env Variablen liegen alle in den CI/CD-Settings.

**Um sie wieder zu deinstallieren muss folgender Befehl ausgeführt werden:**

``` 
helm delete bike-prediction
```

**Achtung**: Sowohl die durch die Installation via Helm erzeugten `Services` als auch `PersistenceVolumeClaims` werden dadurch nicht gelöscht! Das heißt, im Falle einer neuen Installation ist die Datenbank bereits initialisiert. Um einen cleanen Re-Install durchzuführen (**Und alle databases, Daten, Nutzer, etc. aus der DB zu löschen**) muss zusätzlich noch folgendes ausgeführt werden:

```
#fish
kubectl delete (kubectl get pvc,ep,service,secret -l release=bike-prediction -o name)
```

```
#bash
kubectl delete $(kubectl get pvc,ep,service,secret -l release=bike-prediction -o name)
```

**Updaten eines Releases:**
``` 
helm upgrade bike-prediction .
```

#### Folgende Services sind implementiert:

- `timescaledb`

    **Zeitreihen basierte Datenbank**
    
    Für Zugriff auf DB innerhalb des Clusters:
    ```
    kubectl exec --stdin --tty bike-prediction-timescaledb-0 -- /bin/bash                                                                            (s4ki_2) 
    ```

- `initdb`

    Erstellt neue Datenbank und Nutzer und legt Tabellen an.

- `datacollector`

    Fragt die nextbike API alle 5 Minuten für Leipzig ab und dumped die Antwort als JSON in den Bucket Store (Minio).

- `preprocessing`

    Holt die neuen Daten aus dem Bucket Store (MinIO) alle halbe Stunde, bereitet sie auf, indem der Service ein JQ Script über die JSON-Dateien laufen lässt, der die relevanten Daten extrahiert. Ermittelt mittels Geocoding [H3-Werte](https://h3geo.org/) für die jeweiligen Positionen, über die sich später aggregieren lässt und füllt einmalig eine Tabelle mit Informationen über die Nextbike-Stationen.

- `train`
    
    Führt jede Stunde das Training aus und speichert die Predictions für die kommenden 3 Stunden in einer Tabelle.
    Die Ergebnisse eines bestimmten Zeitpunkts können repliziert werden, indem man die historischen Daten bis zu diesem Zeitpunkt in das Training einbezieht und den Randomseed 42 verwendet.
    
  
- `fastapi`

    Stellt eine API bereit, über die die aktuellsten Predictions aus der Tabelle gelesen werden können.

    ```https://t8.se4ai.sws.informatik.uni-leipzig.de/pvprediction/{grid_id}/```

    Für die Grid-ID können drei verschiedene Werte eingesetzt werden:

    - Augustusplatz: 881f1a8cb7fffff
    - Lene-Voigt-Park: 881f1a8ca7fffff
    - Clara-Zetkin-Park: 881f1a1659fffff

    Bei den Werten handelt es sich um H3-Hexagons, die eine [Fläche von etwa 0,73 km²](https://h3geo.org/docs/core-library/restable/) umfassen.

    Die Grenzen der Flächen können z.B. auf [dieser Seite](https://wolf-h3-viewer.glitch.me/) eingesehen werden.

    .

- `webapp`
  
    *Todo*