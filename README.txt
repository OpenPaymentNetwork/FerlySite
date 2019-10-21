ferly-backend
=============

Getting Started
---------------

- Change directory into your newly created project.

    cd Ferly

- Create a Python virtual environment.

    python3 -m venv env

- Upgrade packaging tools.

    env/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Create a local ferlyapitest Postgres database owned by your user account.
  The tests require it.

    sudo -u postgres createdb -O ${USER} ferlyapitest

- Run the tests.

    env/bin/nosetests

- Run the project.

    env/bin/pserve --reload staging.ini


Configuring a Database
-----------------------

- Change directory into your project.

    cd Ferly

- Set the database URL as an env var.

    export SQLALCHEMY_URL=postgres://user:deviceToken@url:port/dbname

- Configure the database.

    env/bin/initialize_backend_db staging.ini


Migrating a Database
--------------------

You can execute database migrations from your laptop/desktop (without logging
in to EC2 or Elastic Beanstalk). You just need the SQLALCHEMY_URL for the
environment.

- Change to the backend/database directory.

    cd backend/database

- Set the database URL as an env var.

    export SQLALCHEMY_URL=postgres://user:deviceToken@url:port/dbname

- Use Alembic to upgrade. Replace REVISION with the target schema revision.

    ../../env/bin/alembic upgrade REVISION

Here is an example command for autogenerating a schema migration:

    cd backend/database
    SQLALCHEMY_URL=postgres:///ferlyapi ../../env/bin/alembic revision \
        --rev-id 0011 --autogenerate -m "add field_color"
