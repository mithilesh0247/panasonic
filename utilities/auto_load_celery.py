import subprocess
import time

def load_scheduler():
    p1 = subprocess.Popen('celery purge -f')
    p2 = subprocess.Popen('celery -A scm beat -l info')
    
    while True:
        time.sleep(15)
        for proc in [p1, p2]:
            status = proc.poll()
            if status == None:
                continue
            elif status == 0:
                # harvest the answers
                print("no status")
            else:
                print("command1 failed with status", status)