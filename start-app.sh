#!/usr/bin/env bash

python manage.py waitdb 
python manage.py migrate 
python manage.py createcachetable 
python manage.py collectstatic --no-input --clean
python manage.py loaddata admin_theme_data.json 
python manage.py loaddata openlxp_notifications_template.json 
python manage.py loaddata openlxp_notifications_subject.json 
python manage.py loaddata openlxp_notifications_email.json 
cd /opt/app/ 
pwd 
./start-server.sh 
