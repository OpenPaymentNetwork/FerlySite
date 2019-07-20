#!/bin/sh -e

# Delete and re-create the ferlyapi and ferlyapitest local databases.
# 'sudo' access is required to use this script.

cd "$(dirname $0)"
here="$(pwd)"
cd /
sudo -u postgres dropdb ferlyapi || true
sudo -u postgres createdb -O "${USER}" ferlyapi
sudo -u postgres dropdb ferlyapitest || true
sudo -u postgres createdb -O "${USER}" ferlyapitest
cd "${here}"
env/bin/initialize_backend_db development.ini
