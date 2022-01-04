FROM python:3
RUN apt-get update &&\
 apt-get install -y postgresql-client &&\
 rm -rf /var/lib/apt/lists/*
ENV PYTHONUNBUFFERED 1
WORKDIR /srv/
ADD requirements.txt /srv/
RUN pip install -r requirements.txt
COPY . /srv/
# Edit project name below
WORKDIR /srv/sobituaries/
CMD ../bin/wait postgres --\
 python manage.py collectstatic --noinput &&\
 cp /srv/favicon.ico static/ &&\
 python manage.py runserver 0.0.0.0:8000
