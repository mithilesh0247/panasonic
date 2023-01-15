# 3sc

# for dumping data into json file
python manage.py dumpdata > filename.json
# For specific app
python manage.py dumpdata appname > filename.json


# for loading dumped data into db

python manage.py loaddata filename.json

# TO run celery 
celery -A scm worker -l INFO
# celery task with log
celery -A scm worker --loglevel=info

#CELERY BEAT SERVER
celery -A scm.celery beat