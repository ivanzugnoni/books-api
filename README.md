# books-api

Sample project of a Django API using REST Framework


### Setup

Install dependencies using [Poetry](https://python-poetry.org/docs/)
```
$ poetry install
```

Run Django migrations (make sure to have `PYTHONPATH` and `DJANGO_SETTINGS_MODULE` envvars properly set)
```
$ django-admin migrate
```

Runserver
```
$ django-admin runserver
```

Accessing to `localhost:8000/api/v1` in your web browser will allow you to start using the API playground and perform some queries 🎉
