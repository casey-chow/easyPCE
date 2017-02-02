# easyPCE

A better course evaluation tool.

## Quick Start

Make sure you have Python 2.7, pip, and PostgreSQL, and npm installed. Then, run:

```sh
$ pip install -r requirements/local.txt
$ python manage.py migrate
$ npm install
$ npm run build
```

To run the server:

```sh
$ python manage.py runserver
```

## Development

### Development Tools

If you intend to develop on the build, you may enjoy hot code reloading on the
client side. To set this up, run:

```sh
$ npm run watch &
$ python manage.py runserver
```

Additionally, if you want scraping functionality to work, you'll need too
install Redis and Celery for task scheduling. Then, you can run this:

```sh
$ celery worker -A easypce -l info
$ python manage.py runserver
```

You can also do lots of fun stuff with concurrency if you use [Celery multi]:

[Celery multi]: http://docs.celeryproject.org/en/latest/reference/celery.bin.multi.html

```sh
$ celery multi start num_workers -A easypce -l info
```

### Folder Stucture

This project uses a mostly custom folder structure as an almagamation of
various starting templates, adapted for our specific purposes.

| Folder            | Description
|-------------------|-------------
| `api`             | REST API-related code
| `assets`          | created on `npm run build`, bundle outputs for production use
| `easypce`         | The project folder; Django settings and routes
| `requirements`    | Python requirements, separated by environment
| `static`          | Static assets, including client-side code
| `webpack`         | Webpack configuration

### Build Tasks

- `celery worker -A easypce -l info`: Run a celery worker for the project.
- `celery multi start num_workers -A easypce -l info`: Run a worker cluster for the project.
- `python manage.py runserver`: Run a development server.
- `python manage.py scrape [--all] [--meta] [--terms (terms)]`: Run scraping tasks on workers.
- `npm run build`: Builds the client-side bundle for production use.
- `npm run build-local`: Like above, but for local use.
- `npm run clean`: Remove all generated files.
- `npm run watch`: Launch a server that watches and serves client-side files.

## Thanks

- [Using React with Django, with a little help from Webpack][1]
- [Django REST Framework Tutorial][2]
- [First Steps with Django (Celery)][3]

[1]: https://geezhawk.github.io/using-react-with-django-rest-framework
[2]: http://www.django-rest-framework.org/tutorial/1-serialization/
[3]: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
