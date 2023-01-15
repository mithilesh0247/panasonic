from __future__ import absolute_import, unicode_literals
import os
import pandas as pd
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scm.settings')

TASK_FUNC_MAP = {
    'MSL Planning'              : "MSL_Planning_Func",
    'MSL Reporting'             : "MSL_Reporting_Func",
    'Replenishment Planning'    : "Replenishment_Planning_Func",
    'Replenishment Reporting'   : "Replenishment_Reporting_Func",
    'DOS Calculation'           : "DOS_Calculation_Func",
    'PP Planning'               : "PP_Planning_Func",
}

app = Celery('scm')

    
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')
app.config_from_object(settings, namespace='CELERY')

if os.path.exists('documents/scheduler/csv/data.csv'):
    try:
        df = pd.read_csv("documents/scheduler/csv/data.csv", usecols= ["Name",'DateTime'])
        dateTimeExpList = df.to_dict('list').get('DateTime')
        nameExpList = df.to_dict('list').get('Name')

        schedules = {}
        for task_name, cron_expression in zip(nameExpList, dateTimeExpList):
            splittedExpression = cron_expression.split(" ")
            if len(splittedExpression)==5 :

                minute = splittedExpression[0]
                hour = splittedExpression[1]
                day_of_month = splittedExpression[2]
                month_of_year = splittedExpression[3]
                day_of_week = splittedExpression[4]

                task_func = TASK_FUNC_MAP.get(task_name, None)

                if task_func:
                    schedules = schedules| {
                        'Job Scheduler tasks: '+ task_name +' ': {
                        'task': 'scm_app.tasks.'+task_func+'',
                        'schedule': crontab(hour=hour, minute=minute, day_of_week=day_of_week, day_of_month=day_of_month, month_of_year=month_of_year,),
                    }}
            else:
                print("error : Invalid job task_name: '"+str(task_name)+"' or cron_expression: '"+cron_expression+"'")
                pass
            app.conf.beat_schedule = schedules
    except Exception as e:
        print(e)

# Celery Schedules - https://docs.celeryproject.org/en/stable/reference/celery.schedules.html

    
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    