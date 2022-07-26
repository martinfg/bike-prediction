## Voraussage von Verfügbarkeit von Leih-Fahrrädern

...

### Deployment

In `./services` sind die einzelnen Komponenten gespeichert, meist Python Skripte mit Dockerfiles. Diese müssen per `docker build` gebaut und dann per `docker push` in die private Docker Registry `group8se4ai` gepushed werden. Die Credentials liegen in den GitLab CI/CD-Settings.

**Die Applikation als ganze liegt als Helm chart (`./bike-prediction`) vor. Um sie zu deployen muss folgendes ausgführt werden:**
```
helm install \
--set minio.password=$MINIO_PASSWORD \
--set containerRegistry.dockerconfig=$DOCKER_CONFIG \
--set initdb.credentials.password=$DB_PASSWORD \
bike-prediction . 
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

#### Folgende Services sind implementiert:

- `timescaledb`

    **Zeitreihen basierte Datenbank**
    
    Für Zugriff auf DB innerhalb des Clusters:
    ```
    kubectl exec --stdin --tty bike-prediction-timescaledb-0 -- /bin/bash                                                                            (s4ki_2) 
    ```

- `initdb`

    Initialisiert die Datenbank

- `datacollector`

    Fragt die nextbike Api alle 5 Minuten für Leipzig ab und dumped die Antwort als json in den Bucket Store (Minio).

- `preprocessing`

    *Todo*

- `train`

    *Todo*

- `predict`

    *Todo*
  
- `fastapi`

    *Todo*

- `webapp`
  
    *Todo*