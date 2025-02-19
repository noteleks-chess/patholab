#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn Eldo_pathology_project.wsgi:application