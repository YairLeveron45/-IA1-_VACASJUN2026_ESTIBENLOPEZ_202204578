# Base de datos

La practica usa SQLite para facilitar la ejecucion local y con Docker.

En local, FastAPI usa:

```txt
database/smartbot.db
```

Con Docker Compose, la base se guarda en un volumen llamado `smartbot_data`.
