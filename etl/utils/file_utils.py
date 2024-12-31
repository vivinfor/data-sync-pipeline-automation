import os
from datetime import datetime, timedelta

def clean_old_files(directory, days=30):
    retention_period = timedelta(days=days)
    now = datetime.now()

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if now - file_modified_time > retention_period:
                os.remove(filepath)
