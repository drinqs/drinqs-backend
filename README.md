# Drinqs Backend

## Prerequisites
Python 3.9

PostgreSQL 13.1

pipenv

## Build Setup

###### install dependencies
`pipenv install`

###### activate virtual environment
`pipenv shell`

###### running database migrations (postgresql must be running)
`python3 manage.py makemigrations`

`python3 manage.py migrate`

###### serve at localhost:8000
`python3 manage.py runserver`
