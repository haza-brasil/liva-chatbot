from python:3.6

env PYTHONUNBUFFERED 1

run mkdir /kibanaweb
workdir /kibanaweb

add ./kibanaweb/requirements.txt /kibanaweb/

run pip install -r requirements.txt

add ./kibanaweb /kibanaweb/

env PORT=8080                             \
    ALLOWED_HOSTS=localhost               \
    PREFIX_URL=

cmd python manage.py runserver 0.0.0.0:$PORT
