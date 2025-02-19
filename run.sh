#!/bin/bash
python manage.py migrate
python manage.py createsuperuser --noinput
gunicorn Eldo_pathology_project.wsgi:application