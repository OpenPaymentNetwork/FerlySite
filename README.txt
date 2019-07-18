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

- Set the database url as an env var.

    export SQLALCHEMY_URL=postgres://user:password@url:port/dbname

- Configure the database.

    env/bin/initialize_backend_db staging.ini
