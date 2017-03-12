#!/bin/bash

. /uwsgi/bin/activate
cd /mysite
python manage.py syncdb --noinput
echo "from django.contrib.auth.models import User; User.objects.all().delete(); User.objects.create_superuser('$DJANGOUSER', '$DJANGOEMAIL', '$DJANGOPASSWORD')" | \
    python manage.py shell