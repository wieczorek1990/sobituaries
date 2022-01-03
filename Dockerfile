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
# Edit project name below
CMD ../bin/wait postgres --\
 python manage.py migrate &&\
 uwsgi --http 0.0.0.0:8000 --wsgi-file sobituaries/wsgi.py --master --processes 32 --threads 8
