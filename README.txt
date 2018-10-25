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

- Configure the database.

    env/bin/initialize_backend_db development.ini

- Run your project's tests.

    env/bin/nosetests

- Run your project.

    env/bin/pserve development.ini
