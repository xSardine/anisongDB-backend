# Installation guide

> TODO

Make sure to rename the database from `app/data/enhanced_amq_database_nerfed` to `app/data/enhanced_amq_database` before anything else.

## Development Environment

### Install Redis

You will need to install [Redis](https://redis.io/docs/getting-started/installation/install-redis-on-linux/)  
Redis is used to temporarily cache the IP adresses of the users to implement a rate limiter.  

If you are on Windows, follow this [guide](https://redis.io/docs/getting-started/installation/install-redis-on-windows/) to install Redis.

Once Redis is installed, start it, it will run by default on port 6379 :

```shell
sudo service redis-server start
```

### API Local Environment

You will need [Python](https://www.python.org/downloads/)

Then, install poetry :

```shell
pip install poetry
```  

Run the following commands to install the dependencies and start the application :

```shell
poetry install
```

Configure the `.env` file if needed.

Then, start the application with :

```shell
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## API Production Environments

### Using Docker

Build your own image :

```shell
docker build -t anisongdb-api .
```

Configure the `.docker.env` file if needed.

Then run with docker :

```shell
docker compose --env-file .docker.env up
```

### Using Gunicorn

Install dependencies and configure the `.env` file similarly to local environment.  
Then run directly using gunicorn :

```shell
gunicorn --keyfile=</path_to_privkey/privkey.pem> --certfile=</path_to_fullchain/fullchain.pem> -k uvicorn.workers.UvicornWorker main:app --bind=<ip_adress>
```
