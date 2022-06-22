# Sobituaries

## Envs

Create `/envs/` directory using `/envs.example/` as template.

```bash
cp -r envs.example envs
```

Edit envs.

```bash
# django
DJANGO_DEBUG # 0 or 1 for disabled/enabled
DJANGO_SECRET_KEY # 50 characters

# postgres
POSTGRES_USERNAME # username
POSTGRES_PASSWORD # password
```

Use [generator](https://djecrety.ir) for generating `DJANGO_SECRET_KEY`.

## Running

After creating envs run:

```bash
docker compose up
```

This starts with failure when database is yet not created.

Running frontend:

```bash
cd website/
python3 -m http.server 8888
```

## Database

Setting up database, e.g. for local instance:

```bash
docker compose up
docker compose exec postgres bash
psql -h postgres -U postgres  # password is postgres
CREATE DATABASE sobituaries WITH OWNER postgres ENCODING 'utf-8';
```

Running migrations:

```bash
docker compose up
docker compose exec django bash
./manage.py migrate
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
./manage.py dumpdata --format=yaml api.CemeteryRegister > api/fixtures/CemeteryRegister.yaml
./manage.py loaddata CemeteryRegister
```

## Favicon generation

```bash
convert -background none favicon.svg -define icon:auto-resize favicon.ico
```

## Server

Server is on Fedora.

[PostgreSQL](https://docs.fedoraproject.org/en-US/quick-docs/postgresql/):

```bash
sudo -u postgres psql
CREATE user sobituaries WITH password '{password}';
CREATE DATABASE sobituaries WITH OWNER sobituaries ENCODING 'utf-8';
psql -h localhost -d sobituaries -U sobituaries -W
```

Nginx needed:

```bash
chcon -Rt httpd_sys_content_t /srv/sobituaries/website/ /srv/sobituaries/sobituaries/static/
chcon -Rt httpd_sys_content_t /etc/nginx/nginx.conf
setsebool -P httpd_can_network_connect 1
```

## Local tunnel

```bash
npm install -g localtunnel

python3 -m http.server 8001
sudo lt --port 8001
```
