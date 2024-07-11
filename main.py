'''

This program is a desktop deadline notifier

'''

from pynotifier import Notification, NotificationClient
from pynotifier.backends import platform
from tzlocal import get_localzone, get_localzone_name
from pytz import timezone
from pathlib import Path
import datetime
import json
import os
import sys

def clear():
    return os.system('cls')

def pause():
    return os.system('pause')

def close():
    clear()
    return sys.exit()

class DeadlineCalendar:
    def __init__(self, deadlines: dict, json_file: Path, tz_local=get_localzone_name(), time_format='%m/%d/%Y - %H:%M'):
        self.deadlines = deadlines
        self.json_file = json_file
        self.tz_local = tz_local
        self.time_format = time_format
        self.deadline_info = ['First Name', 'Last Name', 'E-mail', 'Phone']
        self.deadlines_list = []

        # Will convert the deadlines strings into datetime
        for deadline in deadlines['deadlines']:
            datetime_converted = datetime.datetime.strptime(deadline['Date_Time'], time_format)
            
            # Will change according to local timezone
            if deadline['TZ'] != tz_local:
                datetime_converted = datetime_converted.astimezone(timezone(tz_local))
            
            self.deadlines_list.append(datetime_converted)

if __name__ == '__main__':
    FILE_PATH = Path(__file__).absolute().parent
    DEADLINES_PATH = FILE_PATH / 'deadlines.json'

    # Loads calendar data from deadlines.json, creates new file if it doesn't exist
    try:
        with open(DEADLINES_PATH, 'r') as f:
            data = json.load(f)
    except(FileNotFoundError):
        with open(DEADLINES_PATH, 'w+') as f:
            f.write('{'
                    '"deadlines": ['
                        '{'
                            '"Date_Time": "01/01/2024 - 00:00",'
                            '"TZ": "UTC"'
                        '}'
                                ']'
                    '}')
            f.seek(0)
            data = json.load(f)

test = DeadlineCalendar(data, DEADLINES_PATH)