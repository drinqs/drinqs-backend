# Drinqs Backend

## Prerequisites

Docker

## Build Setup

#### Build Container

`bin/compose build`

#### serve at localhost:8000

`bin/dev`

#### running database migrations

`bin/manage makemigrations`

`bin/manage migrate`

## Further Commands

- `bin/manage <command>` equals `python manage.py <command>`
- `bin/exec <command>` equals `bin/compose exec app  <command>`
- `bin/compose <command>` equals `docker-compose <command>` (uses full docker stack with sync and development files)
