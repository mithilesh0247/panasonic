from celery import shared_task
from . utils import mslReport
from scm.celery import app

@shared_task
def test_func() -> None:
    import logging
    logging.info("Testing......")
    print("Welcome in Shared Task")
    for i in range(10):
        print(i)
    return True

@shared_task
@app.task
def MSL_Reporting_Func()-> None:
    print("Job_name: MSL_Reporting_Func")
    data = mslReport()
    print(data)
    # return data


@shared_task
@app.task
def MSL_Planning_Func():
    print("Job_name: MSL_Planning_Func")


@shared_task
@app.task
def Replenishment_Planning_Func():
    print("Job_name: Replenishment_Planning_Func")


@shared_task
@app.task
def Replenishment_Reporting_Func():
    print("Job_name: Replenishment_Reporting_Func")


@shared_task
@app.task
def DOS_Calculation_Func():
    print("Job_name: DOS_Calculation_Func")


@shared_task
@app.task
def PP_Planning_Func():
    print("Job_name: PP_Planning_Func")

