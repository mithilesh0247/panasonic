import os
from scm_app.models import *

PATHS = [
    'documents/scheduler/csv',
]

def auto_path():
    '''
    create path needs to be created if not created yet
    '''
    for path in PATHS:
        if not(os.path.exists(path)):
            os.makedirs(path)
            print(path+": created.")
            
def run():
    auto_path()