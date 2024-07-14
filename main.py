'''

This program is a desktop deadline notifier

'''

from pynotifier import Notification, NotificationClient
from pynotifier.backends import platform
from tzlocal import get_localzone_name
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

def modified_time(file: Path):
    return os.path.getmtime(file)

class DeadlineCalendar:
    def __init__(self, deadlines: dict, json_file: Path, tz_local=get_localzone_name(), time_format='%m/%d/%Y - %H:%M'):
        self.deadlines = deadlines
        self.json_file = json_file
        self.json_file_mtime = modified_time(json_file)
        self.tz_local = tz_local
        self.time_format = time_format
        self.deadline_info = ['Month', 'Day', 'Year', 'Hours', 'Minutes']
        self.deadlines_list = []
        self.menu_choices = {('A', 'ADD', '[A]dd deadline'): self.add,
                ('R', 'REMOVE', '[R]emove deadline'): self.remove,
                ('S', 'SEE', '[S]ee deadlines'): self.see,
                ('C', 'CLOSE', '[C]lose the calendar'): close,
                ('T', 'TURN ON', '[T]urn on the notifier'): self.on}

        # Will convert the deadlines strings into datetime
        for deadline in deadlines['deadlines']:
            datetime_converted = datetime.datetime.strptime(deadline['Date_Time'], time_format)
            
            # Will change according to local timezone
            if deadline['TZ'] != tz_local:
                datetime_converted = datetime_converted.astimezone(timezone(tz_local))
            
            self.deadlines_list.append(datetime_converted)
        
    # Adds a deadline
    def add(self):
        # Creates the new deadline temporarily
        temp_deadline = {}
        for info in self.deadline_info:
            clear()
            temp_info = input(f'{info}: ')
            temp_deadline[info] = int(temp_info)
        clear()

        # Converts temporary deadline info into datetime, string and a dictionary
        temp_deadline_datetime = datetime.datetime(temp_deadline['Year'], temp_deadline['Month'], temp_deadline['Day'],
                                                   temp_deadline['Hours'], temp_deadline['Minutes'], tzinfo=timezone(self.tz_local))
        temp_deadline_str = temp_deadline_datetime.strftime(self.time_format)
        temp_deadline_dict = {'Date_Time': temp_deadline_str, 'TZ': self.tz_local}

        # Saves the new deadline
        confirmation = input('Are you sure you want to create this deadline? (Y/N): ').upper()
        if confirmation.startswith('Y'):
            self.deadlines_list.append(temp_deadline_datetime)
            self.deadlines['deadlines'].append(temp_deadline_dict)
            json_deadlines = json.dumps(self.deadlines)
            with open(self.json_file, 'w+') as f:
                f.truncate(0)
                f.seek(0)
                f.write(json_deadlines)
                f.seek(0)
        clear()

    # Removes a deadline
    def remove(self):
        # Checks if there are deadlines
        clear()
        if not self.deadlines['deadlines']:
            print('There are no deadlines to delete...\n')
            pause()
            clear()
            return

        # Indexes the deadlines and then asks the user which one it wants to select
        index = 1
        for deadline in self.deadlines['deadlines']:
            print(f"{index} - {deadline['Date_Time']}")
            index += 1
        to_delete = input('\nWhich deadline would you like to delete? (ID Number): ')
        clear()

        # Deletes the contact
        confirmation = input('Are you sure you want to delete this deadline? (Y/N): ').upper()
        if confirmation.startswith('Y'):
            try:
                # Validates selected deadline
                to_delete = int(to_delete)
                if to_delete <= 0:
                    raise ValueError('Index has to be bigger than 0')
                to_delete -= 1
                self.deadlines_list.pop(to_delete)
                self.deadlines['deadlines'].pop(to_delete)
                json_deadlines = json.dumps(self.deadlines)
                with open(self.json_file, 'w+') as f:
                    f.truncate(0)
                    f.seek(0)
                    f.write(json_deadlines)
                    f.seek(0)
            except(ValueError, IndexError):
                clear()
                print('Invalid deadline ID...\n')
                pause()
        clear()

    # See deadlines
    def see(self):
        clear()
        index = 1
        for deadline in self.deadlines['deadlines']:
            print(f'{index} - {deadline["Date_Time"]}')
            index += 1
        print()
        pause()
        clear()

    # Turn ON deadline alarm
    def on(self):
        while True:
            # Gets time now and checks if json file has been modified
            datetime_now_converted = datetime.datetime.now(timezone(self.tz_local)).strftime(self.time_format)
            recent_json_mtime = modified_time(self.json_file)
            if recent_json_mtime != self.json_file_mtime:
                clear()
                try:
                    with open(self.json_file, 'r') as f:
                        self.deadlines = json.load(f)
                except(FileNotFoundError):
                    print('deadlines.json file not found...\n')
                    pause()
                    continue
            # Checks if time now matches a deadline, notifies the user if it does, and then deletes the deadline
            for index, deadline in enumerate(self.deadlines['deadlines']):
                if deadline['Date_Time'] == datetime_now_converted:
                    print('BEEEEEEP')
                    self.deadlines['deadlines'].pop(index)
                    json_deadlines = json.dumps(self.deadlines)
                    with open(self.json_file, 'w+') as f:
                        f.truncate(0)
                        f.seek(0)
                        f.write(json_deadlines)
                        f.seek(0)

    # Brings up a menu to use the calendar
    def menu(self):
        clear()
        while True:
            choices_str = ''
            for choice in self.menu_choices.keys():
                choices_str += f'{choice[-1]} | '
            choices_str = choices_str[:-3]
            print(f'What would you like to do with your calendar?\n\n{choices_str}\n')
            choice_selected = input().upper()

            for choice in self.menu_choices.keys():
                if choice_selected in choice:
                    self.menu_choices[choice]()

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

calendar = DeadlineCalendar(data, DEADLINES_PATH)
calendar.add()
calendar.on()