# easyPCE

A better course evaluation tool.

## Installation and Running

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

If you intend to develop on the build, you may enjoy hot code reloading on the
client side. To set this up, run:

```sh
$ npm run watch &
$ python manage.py runserver
```

## Folder Stucture

This project uses a mostly custom folder structure as an almagamation of
various starting templates, adapted for our specific purposes.

| Folder            | Description
|-------------------|-------------
| `api`             | REST API-related code
| `easypce`         | The project folder; Django settings and routes
| `requirements`    | Python requirements, separated by environment
| `static`          | Static assets, including client-side code
| `webpack`         | Webpack configuration

## Thanks

- [Using React with Django, with a little help from Webpack](https://geezhawk.github.io/using-react-with-django-rest-framework)
- [Django REST Framework Tutorial](http://www.django-rest-framework.org/tutorial/1-serialization/)

---

## How to Use

To use this project, follow these steps:

1. Create your working environment.
2. Install Django (`$ pip install django`)
3. Create a new project using this template

## Creating Your Project

Using this template to create a new Django app is easy::

    $ django-admin.py startproject --template=https://github.com/heroku/heroku-django-template/archive/master.zip --name=Procfile helloworld

You can replace ``helloworld`` with your desired project name.

## Deployment to Heroku

    $ git init
    $ git add -A
    $ git commit -m "Initial commit"

    $ heroku create
    $ git push heroku master

    $ heroku run python manage.py migrate

See also, a [ready-made application](https://github.com/heroku/python-getting-started), ready to deploy.

## Further Reading

- [Gunicorn](https://warehouse.python.org/project/gunicorn/)
- [WhiteNoise](https://warehouse.python.org/project/whitenoise/)
- [dj-database-url](https://warehouse.python.org/project/dj-database-url/)
