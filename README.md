# Sobituaries

## Envs

Create `/envs/` directory using `/envs.example/` as template.

```bash
# django
DJANGO_DEBUG # 0 or 1 for disabled/enabled
DJANGO_SECRET_KEY # 50 characters

# postgres
POSTGRES_USERNAME # username
POSTGRES_PASSWORD # password
```

## Running

After creating envs run:

```bash
docker compose up
```

This starts with failure when database is yet not created.

## Database

Setting up database, e.g. for local instance:

```bash
docker compose up
docker compose exec postgres bash
psql -h postgres -U postgres  # password is postgres
CREATE DATABASE sobituaries WITH OWNER postgres ENCODING 'utf-8';
```

Now run `docker compose up` again for backend to start without failure.

## Tests

Running tests:

```bash
docker compose up
docker compose exec django bash
./manage.py test api.tests
```

## Deployment

Deploy to production:

* create configuration (look into `/docker compose.yml` and `/Dockerfile`)
    * generate envs (look into `/envs/`)
    * generate Django secret with `pwgen -sy 50 1`

## Management

Managing application:

```bash
docker compose up
docker compose exec django bash
./manage.py createsuperuser
./manage.py collectstatic
```
