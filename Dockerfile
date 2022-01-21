# DEBIAN
# FROM python:3.10.1
# RUN apt-get update &&\
#  apt-get install -y postgresql-client build-essential gcc python3-dev &&\
#  rm -rf /var/lib/apt/lists/*

# ALPINE
FROM python:3.10.1-alpine3.15
RUN apk add bash postgresql-client musl-dev gcc python3-dev libffi-dev &&\
 rm -rf /var/cache/apk/*

ARG PROJECT_NAME
ENV PYTHONUNBUFFERED 1

WORKDIR /srv/
ADD requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

WORKDIR /srv/$PROJECT_NAME/
CMD ../bin/wait postgres --\
 python manage.py collectstatic --noinput &&\
 python manage.py runserver 0.0.0.0:8000 --insecure
