#!/bin/bash -e

# Package the Ferly API for deployment on Elastic Beanstalk.

cd $(dirname $0)

cd frontend
#npm run deploy
cd ..

mkdir -p dist
fn="dist/ferlyapi.zip"
rm -f ${fn}
zip -r ${fn} \
    backend frontend *.txt *.in *.ini *.py .ebextensions \
    -x '*.pyc' '*/__pycache__/*' '*.pyo' 'frontend/node_modules/*'
