# Installation guide

> TODO

Make sure to rename the database from Enhanced-AMQ-Database-Nerfed to Enhanced-AMQ-Database before running the application.

### Start locally

```shell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Start in Production

Using a let's encrypt certificate :

```shell
sudo gunicorn --keyfile=</path_to_privkey/privkey.pem> --certfile=</path_to_fullchain/fullchain.pem> -k uvicorn.workers.UvicornWorker main:app --bind=<ip_adress>
```
