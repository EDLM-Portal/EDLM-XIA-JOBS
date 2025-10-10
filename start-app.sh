#!/usr/bin/env bash

python3 manage.py waitdb 
python3 manage.py migrate 
python3 manage.py createcachetable 
python3 manage.py collectstatic 
python3 manage.py loaddata admin_theme_data.json 
python3 manage.py loaddata openlxp_notifications_template.json 
python3 manage.py loaddata openlxp_notifications_subject.json 
python3 manage.py loaddata openlxp_notifications_email.json 
cd /opt/app/ 
pwd 
./start-server.sh 
