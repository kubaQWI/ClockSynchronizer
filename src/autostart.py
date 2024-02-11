from datetime import datetime
from time import sleep
import configparser
import win32api
import json
import requests
import ctypes
import sys
import os

# Logging officially wyjebaned. Too much problems with it. Probably will sleep better without it

if sys.platform == 'win32':
    print("You are using Windows platform.\n")
    sleep(0.5)
    os.system('cls')
else:
    print("This autostart file is only for windows system.")
    exit()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
# Configuration file

config = configparser.ConfigParser()

user_name = os.getlogin()
cfg_path = f"C:\\Users\\{user_name}\\Documents\\ClockSynchronizer\\config.ini"
config.read(cfg_path)

isDefault = config.get('default', 'isdefault')

if isDefault == 'True':
    timezone = config.get('default', 'default_timezone')
elif isDefault == 'False':
    timezone = config.get('custom', 'timezone')
else:   
    print("Error with config.ini. Please run 'main.py'.")
    sleep(5)
    
response_api = requests.get(f'https://timeapi.io/api/Time/current/zone?timeZone={timezone}')
data = response_api.text
parse_json = json.loads(data)

# Parser

try:
    api_hour = parse_json['hour']
    if api_hour == 0 or api_hour == -1: # Checks if api_hour is 0 (midnight) because it cannot be -1 hour duh
        api_hour = 24
    api_minute = parse_json['minute']
    api_second = parse_json['seconds']
    api_millisecond = parse_json['milliSeconds']

    api_year = parse_json['year']
    api_month = parse_json['month']
    api_day = parse_json['day']

except KeyError:
    print("err.. Something most likely wrong with given timezone or error with an api.")
    sleep(2)
    exit()

now = datetime.now()
    
# Local time

hour = now.hour
minute = now.minute
second = now.second
day = now.day
month = now.month
year = now.year

# print("Global hour: ", api_hour, "Local hour: ", hour) # <-- debug

# Checks if year, month, day, hour and minute are the same as global time.

if api_hour != hour or api_minute != minute or api_day != day or api_month != month or api_year != year: # for now i am leaving this but in 100% later i will change this
    
    if is_admin():
        try:
            print(f"Current timezone: {timezone}")
            win32api.SetSystemTime(api_year, api_month, 0, api_day, api_hour - 1, api_minute, api_second, api_millisecond) # The reason for -1 in api_hour is probably because there is daylight saving time and not standard time. or this is timezone thing idk
        except Exception as e:
            print(e)
            sleep(60)
        print("Successfully updated!")
        sleep(2)
        exit()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    
else:
    print("You are up to date!")
    sleep(2)