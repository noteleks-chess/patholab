#!/bin/bash
python manage.py migrate
gunicorn Eldo_pathology_project.wsgi:application