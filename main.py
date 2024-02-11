from datetime import datetime
from time import sleep
import os
import sys
import json
import shutil
import ctypes
import configparser

# Platform checking

if sys.platform == 'win32':
    print('You are using Windows platform.\n')
else:
    print(f"Using {sys.platform}. This script is not (yet) supported.")
    exit()


try:
    import win32api
except ModuleNotFoundError:
    print("You don't have 'win32api' library. Downloading...") # I know that this is kind of retarded method but I am really tired 
    os.system("pip install pywin32")

try:
    import requests
except ModuleNotFoundError:
    print("You don't have 'requests' library. Downloading...") # xdd i will change that in future edit: probably not. too much work
    os.system("pip install requests")

os.system("cls")

# change directory

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Def section

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def copy_to_autostart_new(file_name):
    user_name = os.getlogin()
    directory = f"C:\\Users\\{user_name}\\Documents\\ClockSynchronizer"

    try:

        os.mkdir(directory)
        directory = directory
        shutil.copy(file_name, directory)

    except FileExistsError:

        directory = directory
        shutil.copy(file_name, directory)

def copy_to_as(file_name):

    user_name = os.getlogin()
    directory = f"C:\\Users\\{user_name}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    shutil.copy(file_name, directory)

# Checks if program was run as admin

if is_admin():
    pass
else:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    exit()

# Configuration for default settings

user_name = os.getlogin() # i know this is so random spot but i dont have other idea where to put it

config = configparser.ConfigParser()

cfg_path = f"C:\\Users\\{user_name}\\Documents\\ClockSynchronizer\\"
config.read(cfg_path + 'config.ini')

if os.path.exists(cfg_path + 'config.ini') == True: # for some reason it doesn't work xddd i will later fix it
    try:
        defaultTimezone = config.get('default', 'default_timezone')
        isDefault = config.get('default', 'isdefault')
    except (configparser.NoOptionError, configparser.NoSectionError) as e:
        print(str(e)) # <-- debug
        os.remove(cfg_path + 'config.ini')
        print("Config file does not have essential arguments. Restarting app...")
        sleep(2)
        os.startfile("main.py")
        exit()
else:
    if os.path.exists(cfg_path) == False:
        os.mkdir(cfg_path)

    config['default'] = {'default_timezone': 'Europe/Warsaw',
                     'isdefault': True}
    
    with open(cfg_path + 'config.ini', 'w') as configfile:
        config.write(configfile)
        configfile.close()
    
isDefault = config.get('default', 'isdefault')

# Basic checking if default values are in config.ini file.

if isDefault == 'True':
    timezone = config.get('default', 'default_timezone')
elif isDefault == 'False':
    timezone = config.get('custom', 'timezone')
else:
    os.remove(cfg_path + 'config.ini')
    print("Error, config.ini is damaged. ")
    os.startfile('main.py')
    exit()

# Choice
choices = ['1', '2', '3', '4', '5']

while True:
    choice = input("[1] Check if your local clock is synchronized with global clock.\n[2] Autostart for synchronizer.\n[3] Delete autostart.\n[4] Modify time zone.\n[5] Reset config.ini file.\n\n> ")
    if choice in choices:
        break
    else:
        print(f"\nThere is no choice such as '{choice}'.\n")
        continue

if choice == '1':

    # Grabs api information from Europe/Warsaw or other time zone.

    response_api = requests.get(f'https://timeapi.io/api/Time/current/zone?timeZone={timezone}')
    data = response_api.text
    parse_json = json.loads(data)

    # Parser
    try:

        api_hour = parse_json['hour'] 
        api_minute = parse_json['minute']
        api_second = parse_json['seconds']
        api_millisecond = parse_json['milliSeconds']

        api_year = parse_json['year']
        api_month = parse_json['month']
        api_day = parse_json['day']

        if api_hour == 0:
            api_hour = 24

    except KeyError:
        print("err.. Something is wrong most likely with given timezone or error with an api.")
        sleep(3)
        exit()

    print(f"Current timezone: {timezone}\n")

    print(f"Current time: {api_hour}:{api_minute}:{api_second}\n") # <-- debug

    now = datetime.now()
    
    # Local time

    hour = now.hour
    minute = now.minute
    second = now.second
    day = now.day
    month = now.month
    year = now.year

    print(f"Local time: {hour}:{minute}:{second}\n") # <-- debug
    
    # Checks if hour, minute and second are synchronized

    if api_hour != hour or api_minute != minute:

        print("Your clock is not synchronized!\n")
        while True:

            asdf = ['y', 't', 'n']
            syn_ch = input("Do you want to synchronize clock? [Y/N]: ") # there is a bug that if user will wait for few minutes it will actually not get accurate time.
            syn_ch = syn_ch.lower()

            if syn_ch in asdf:

                if syn_ch == "y" or syn_ch == 't':
                    try:
                        win32api.SetSystemTime(api_year, api_month, 0, api_day, api_hour - 1, api_minute, api_second, api_millisecond)
                    except Exception as e:
                        print("No admin priviles!")
                        sleep(3)
                    print("Successfully changed!")
                    sleep(3)
                    break
                else:

                    break

    else:

        inaccuracy = [-1, 0, 1]
        comparison = api_second - second

        if comparison in inaccuracy: # Checks if numbers -1, 0 or 1 are the result of api_second - second

            print("Your clock is synchronized perfectly!")
            sleep(3)

        else:

            print(f"Your local time is delayed by {comparison} seconds.") # If they are not then show the result
            sleep(3)
        
elif choice == '2':
    # I know that there is probably better solution for this but i didn't slept this night so idc.
    try:
        copy_to_autostart_new('./src/autostart.py')
        print("Copied to startup folder!")

        batch_command = "@echo off\ntitle autostart\npython \"%userprofile%/Documents/ClockSynchronizer/autostart.py\""

        with open('./PythonAutostart.bat', 'w') as batch:

            batch.write(batch_command)
            print("Batch file written.") # <-- debug

        copy_to_as("./PythonAutostart.bat")
        os.remove("./PythonAutostart.bat")

        print("Successfully moved automation script!")
        sleep(3)
    except Exception as e:
        print(str(e))
        input("")
elif choice == '3':

    user_name = os.getlogin()
    directory = f"C:\\Users\\{user_name}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    document_dir = f"C:\\Users\\{user_name}\\Documents\\ClockSynchronizer"
    bat_file = 'PythonAutostart.bat'
    document_file = 'autostart.py'

    file_path = os.path.join(directory, bat_file)
    doc_file_path = os.path.join(document_dir, document_file)

    if os.path.exists(file_path) == True:

        os.remove(file_path)

        print(f"Successfully removed {bat_file}.")
    else:
        print(f"File {bat_file} does not exist.")
        
    if os.path.exists(doc_file_path):
        if os.path.isfile(doc_file_path):
            os.remove(doc_file_path)
            print(f"Successfully removed {document_file}")
        else:
            print(f"File {document_file} does not exist.")
    else:
        print(f"File {document_file} does not exist.")
    
    print("Successfully deleted all files!")
    sleep(3)

elif choice == '4':
    timezones = []

    with open('./src/timezone.txt', 'r') as timezones_file:

        lines = timezones_file.readlines()

        for timezone_lines in lines:

            country_code, timezone = timezone_lines.strip().split('\t')
            timezones.append(timezone)
            print(f"Country Code: {country_code}, Timezone: {timezone}")
            
    while 1:

        custom = input("\nInput a timezone (CTRL + F to find string): ")
        found = False
        custom = custom.lstrip("'")
        config_default_false = 'isdefault = True'

        if custom in timezones:

            config['default'] = {'default_timezone': 'Europe/Warsaw',
                     'isdefault': False}
            config['custom'] = {'timezone' : custom}
    
            with open(cfg_path + 'config.ini', 'w') as configfile:
                config.write(configfile)
            print("Successfully updated!")

            sleep(3)
            break
        elif custom not in timezones:

            print(f"Couldn't find '{custom}' timezone. Try again")
            continue

elif choice == '5':
    lists = ['y', 'Y', 'n', 'N']
    while True:
        choice2 = input("Are you sure that you want to reset config file? [Y/N]: ")
        if choice2 in lists:
            break
        else:
            print(f"There is no such thing as {choice2}. Try again.")
    choice2.lower()
    if choice2 == 'y':
        os.remove(cfg_path + 'config.ini')
        config['default'] = {'default_timezone': 'Europe/Warsaw',
                     'isdefault': True}
    
        with open(cfg_path + 'config.ini', 'w') as configfile:
            config.write(configfile)
        print("Successfully reset!")
        sleep(3)
    else:
        pass
