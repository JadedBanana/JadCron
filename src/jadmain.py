import gc
import os
import json
import time
import random
import psutil
import shutil
import datetime
import pyautogui
from calendar import isleap
from ast import literal_eval
from threading import Thread

__author__ = 'Jade Godwin'
__version__ = '0.2.8'

today = None


# Handles console logging and file output.
def output(text, file, output_file=None):
    if output_file:
        output_file.write('{}\n'.format(text))
    if text != '\n':
        print(os.path.basename(file) + ': ' + text)
    else:
        print()


import general, files, processes, webpages, hardware, misc


# Actually runs the command iteself.
class command_runner(Thread):
    def __init__(self, commands, args, filename, output_file, command_prefix, repeats):
        Thread.__init__(self)
        self.commands = commands
        self.args = args
        self.filename = filename
        self.file = None
        self.command_prefix = command_prefix
        self.repeats = repeats if repeats else 0
        if type(output_file) is str:
            try:
                self.file = open(output_file, 'a')
            except FileNotFoundError:
                while not os.path.isfile(output_file):
                    try:
                        self.file = open(output_file, 'a')
                    except FileNotFoundError:
                        output_temp = os.path.dirname(output_file)
                        while not os.path.isdir(output_temp):
                            try:
                                os.mkdir(output_temp)
                            except FileNotFoundError:
                                output_temp = os.path.dirname(output_temp)
        output('========================' + today.strftime('%A %Y-%m-%d %H:%M') + '========================',
               self.filename, self.file)
        print(os.path.basename(filename) + ': Output file {}'.format(self.file.name))
        self.start()

    def run(self):
        if type(self.commands) is list:
            skip_count = []
            until_skip_count = []
            skipped_last = False
            args_original = self.args.copy()
            if not type(self.args) is list and (self.args is None or not len(self.args) == len(self.commands)):
                output('Args needs to be an array of equal length to the command array!', self.filename, self.file)
            else:
                for i in range(self.repeats + 1):
                    self.args = args_original.copy()
                    if i != 0:
                        output('===={}{} repeat===='.format(i, 'th' if i%10 > 3 or i%10 == 0 else ('rd' if i == 3 else ('nd' if i == 2 else 'st'))), self.filename, self.file)
                    for command in range(len(self.commands)):
                        self.args[command] = parse_args(self.args[command], self.command_prefix)
                        if type(self.commands[command]) is str:
                            output('{} is not a valid command.'.format(self.commands[command]), self.filename, self.file)
                            break
                        else:
                            command_name = self.commands[command].__name__
                            if len(skip_count) == 0:
                                until_skip_count = []
                            else:
                                while len(until_skip_count) > 0 and until_skip_count[len(until_skip_count) - 1] == 0:
                                    until_skip_count = until_skip_count[:len(until_skip_count) - 1]
                                while len(skip_count) > 0 and skip_count[len(skip_count) - 1] == 0:
                                    skip_count = skip_count[:len(skip_count) - 1]
                                if len(skip_count) == 0:
                                    until_skip_count = []
                                elif len(skip_count) > len(until_skip_count):
                                    skip_count[len(skip_count) - 1] -= 1
                                    skipped_last = True
                                    if command_name == 'conditional_switch':
                                        if not type(self.args[command]) is list or len(self.args[command]) != 3:
                                            output('Skipping command {}. (Would skip commands beneath it, too, but its arguments are invalid!)'.format(command_name), self.filename, self.file)
                                        elif not type(self.args[command][1]) is int:
                                            output('Skipping command {}. (Would skip commands beneath it, too, but its arguments are invalid!)'.format(command_name), self.filename, self.file)
                                        elif not type(self.args[command][2]) is int:
                                            output('Skipping command {}. (Would skip commands beneath it, too, but its arguments are invalid!)'.format(command_name), self.filename, self.file)
                                        else:
                                            output('Skipping command {} and the {} commands beneath it.'.format(command_name, self.args[command][1] + self.args[command][2]), self.filename, self.file)
                                            skip_count[len(skip_count) - 1] += self.args[command][1] + self.args[command][2]
                                    else:
                                        output('Skipping command {}.'.format(command_name), self.filename, self.file)
                                    continue
                                else:
                                    until_skip_count[len(until_skip_count) - 1] -= 1
                            if skipped_last:
                                skipped_last = False
                                output('', self.filename, self.file)
                            output('Running command {0} with arguments {2}{1}{2}.'.format(command_name, self.args[command], '"' if type(self.args[command]) is str else ''), self.filename, self.file)
                            if 'conditional' in command_name:
                                skips, until_skips = self.commands[command](self.file, self.filename, self.args[command])
                                skip_count.append(skips)
                                until_skip_count.append(until_skips)
                                output('', self.filename, self.file)
                            else:
                                self.commands[command](self.file, self.filename, self.args[command])
                                output('', self.filename, self.file)
                    if skipped_last:
                        output('', self.filename, self.file)
        else:
            if type(self.commands) is str:
                output('{} is not a valid command.'.format(self.commands), self.filename, self.file)
            else:
                self.args = parse_args(self.args, self.command_prefix)
                output('Running command {} with arguments {}.'.format(self.commands.__name__, ('"' + str(self.args) + '"') if type(self.args) is str else self.args), self.filename, self.file)
                self.commands(self.file, self.filename, self.args)
        output('\n', self.filename, self.file)
        if self.file:
            self.file.close()


# Argument functions.
class argument_functions():
    function_prefix = '?:>>'
    valid_commands = {
        'year': '''def year(digits = 4):
            year = str(today.year)
            if not type(digits) is int or digits < 1:
                digits = len(year)
            if digits > len(year):
                globals()['return_value'] = '0' * (digits - len(year)) + year
            else:
                globals()['return_value'] = year[len(year) - digits:]''',

        'month': '''def month(style = 0):
            month = today.month
            if style <= 1:
                globals()['return_value'] = ('0' if style == 0 and month < 10 else '') + str(month)
            else:
                months = [['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                          ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']]
                globals()['return_value'] = months[style % 2][month - 1]''',

        'week': '''def week(digits = 2):
            week = str(today.isocalendar()[1])
            if not type(digits) is int or digits < 1:
                digits = 2
            if digits > len(week):
                globals()['return_value'] = '0' * (digits - len(week)) + week
            else:
                globals()['return_value'] = week''',

        'weekday': '''def weekday(style = 0):
            weekday = today.weekday()
            if style == 0:
                globals()['return_value'] = str(weekday)
            else:
                days = [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                        ['Mon', 'Tues', 'Wednes', 'Thurs', 'Fri', 'Sat', 'Sun'],
                        ['Mon', 'Tues', 'Wednes', 'Thur', 'Fri', 'Sat', 'Sun'],
                        ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                        ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
                        ['M', 'T', 'W', 'H', 'F', 'S', 'U'],
                        ['M', 'T', 'W', 'R', 'F', 'S', 'U']]
                globals()['return_value'] = days[(style - 1) % 7][weekday]''',

        'day': '''def day(digits = 2):
            day = str(today.day)
            if not type(digits) is int or digits < 1:
                digits = 2
            if digits > len(day):
                globals()['return_value'] = '0' * (digits - len(day)) + day
            else:
                globals()['return_value'] = day''',

        'hour': '''def hour(digits = 2, military = True):
            hour = today.hour
            if not type(digits) is int or digits < 1:
                digits = 2
            if not military:
                hour%= 12
            if digits > len(str(hour)):
                globals()['return_value'] = '0' * (digits - len(str(hour))) + str(hour)
            else:
                globals()['return_value'] = str(hour)''',

        'minute': '''def minute(digits = 2):
            minute = str(today.minute)
            if not type(digits) is int or digits < 1:
                digits = 2
            if digits > len(minute):
                globals()['return_value'] = '0' * (digits - len(minute)) + minute
            else:
                globals()['return_value'] = minute''',

        'eval': '''def eval(thing):
            if not type(thing) is str:
                globals()['return_value'] = thing
            else:
                globals()['return_value'] = eval(thing)''',

        'read': '''def read(file):
            if not type(thing) is str:
                globals()['return_value'] = thing
            else:
                if os.path.isfile(thing):
                    try:
                        with open(thing, 'r') as file:
                            globals()['return_value'] = file.read()
                    except PermissionError:
                        globals()['return_value'] = thing
                else:
                    globals()['return_value'] = thing''',

        'exists': '''def exists(file):
            if type(file) is list:
                for filz in file:
                    if not exists(filz):
                        globals()['return_value'] = False
                        return False
                globals()['return_value'] = True
                return True
            else:
                if os.path.exists(str(file)):
                    globals()['return_value'] = True
                return True''',

        'sizeof': '''def sizeof(file):
            if type(file) is list:
                total_size = 0
                for filz in file:
                    total_size+= sizeof(filz)
                globals()['return_value'] = total_size
                return total_size
            else:
                if os.path.isdir(str(file)):
                    total_size = 0
                    for filz in os.listdir(file):
                        total_size+= sizeof(os.path.join(file, filz))
                    globals()['return_value'] = total_size
                    return total_size
                elif os.path.isfile(str(file)):
                    globals()['return_value'] = os.path.getsize(str(file))
                    return globals()['return_value']
            globals()['return_value'] = 0    
            return 0''',

        'length': '''def length(strg):
            try:
                globals()['return_value'] = len(strg)
            except TypeError:
                globals()['return_value'] = len(str(strg))''',

        'lower': '''def lower(strg):
            globals()['return_value'] = str(strg).lower()''',

        'upper': '''def upper(strg):
            globals()['return_value'] = str(strg).upper()''',

        'substr': '''def substr(strg, lower_index = 0, upper_index = -1):
            try:
                strg = str(strg)
                lower_index = int(lower_index)
                upper_index = int(upper_index)
            except TypeError:
                globals()['return_value'] = strg
                return
            if lower_index < 0:
                lower_index = 0
            elif lower_index > len(strg):
                lower_index = len(strg)
            if upper_index < 0:
                upper_index = 0
            elif upper_index > len(strg):
                upper_index = len(strg)
            globals()['return_value'] = strg[lower_index:upper_index]''',

        'running': '''def running(process_name):
            globals()['return_value'] = False
            if not type(process_name) is str:
                process_name = str(process_name)
            for proc in psutil.process_iter():
                try:
                    if process_name.lower() in proc.name().lower():
                        globals()['return_value'] = proc.is_running()
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass''',

        'running2': '''def running2(pid):
            globals()['return_value'] = False
            try:
                pid = int(pid)
            except ValueError:
                return
            for proc in psutil.process_iter():
                try:
                    if pid == proc.pid:
                        globals()['return_value'] = proc.is_running()
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass''',

        'pid': '''def pid(process_name):
            globals()['return_value'] = -1
            if not type(process_name) is str:
                process_name = str(process_name)
            for proc in psutil.process_iter():
                try:
                    if process_name.lower() in proc.name().lower():
                        globals()['return_value'] = proc.pid
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass''',

        'processname': '''def processname(pid):
            globals()['return_value'] = None
            try:
                pid = int(pid)
            except ValueError:
                return
            for proc in psutil.process_iter():
                try:
                    if pid == proc.pid:
                        globals()['return_value'] = proc.name()
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass''',

        'countinstances': '''def countinstances(process_name):
            globals()['return_value'] = 0
            if not type(process_name) is str:
                process_name = str(process_name)
            for proc in psutil.process_iter():
                try:
                    if process_name.lower() in proc.name().lower():
                        globals()['return_value'] += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass''',

        'random': '''def random():
            globals()['return_value'] = random.random()''',

        'choice': '''def choice(text='', title='Confirm', buttons=['OK', 'Cancel']):
            if not type(buttons) is list:
                buttons = [buttons]
            for i in range(len(buttons)):
                buttons[i] = str(buttons[i])
            globals()['return_value'] = pyautogui.confirm(str(text), str(title), buttons)''',

        'input': '''def input(text = '', title = 'Input', default = ''):
            globals()['return_value'] = pyautogui.prompt(str(text), str(title), str(default))''',

        'password': '''def password(text = '', title = 'Password', default = '', mask = '*'):
            globals()['return_value'] = pyautogui.password(str(text), str(title), str(default), str(mask))''',

        'pixel': '''def pixel(x, y):
            try:
                globals()['return_value'] = list(pyautogui.pixel(int(x), int(y)))
            except (TypeError, OSError):
                globals()['return_value'] = None''',

        'colormatches': '''def colormatches(x, y, r, g, b, tolerance = 0):
            try:
                globals()['return_value'] = pyautogui.pixelMatchesColor(int(x), int(y), (r, g, b), tolerance)
            except (TypeError, OSError):
                globals()['return_value'] = False''',

        'colormatches2': '''def colormatches2(x, y, rgb, tolerance = 0):
            try:
                globals()['return_value'] = pyautogui.pixelMatchesColor(int(x), int(y), tuple(rgb), int(tolerance))
            except (TypeError, OSError):
                globals()['return_value'] = False''',

        'colormatches3': '''def colormatches3(x1, y1, x2, y2, tolerance = 0):
            rgb = None
            try:
                rgb = pyautogui.pixel(int(x1), int(y1))
            except (TypeError, OSError):
                globals()['return_value'] = False
                return
            try:
                globals()['return_value'] = pyautogui.pixelMatchesColor(int(x2), int(y2), rgb, int(tolerance))
            except (TypeError, OSError):
                globals()['return_value'] = False'''
    }

    @staticmethod
    def go_arg_commands(argument, function_prefix):
        if function_prefix in argument:
            last_index = len(argument)
            while argument.rfind(function_prefix, 0, last_index) != -1:
                last_index = argument.rfind(function_prefix, 0, last_index)
                cmd = argument[last_index:].replace(function_prefix, '')
                try:
                    found_cmd = False
                    for real_cmd in argument_functions.valid_commands:
                        if cmd[:len(real_cmd)] == real_cmd and cmd[len(real_cmd)] == '(':
                            found_cmd = True
                            break
                    if not found_cmd:
                        continue
                    parenthesis_depth = 1
                    in_string_char = None
                    index = len(real_cmd)
                    while (parenthesis_depth > 0):
                        index += 1
                        if in_string_char:
                            if cmd[index] == in_string_char:
                                in_string_char = None
                            continue
                        elif cmd[index] == '"' or cmd[index] == "'":
                            in_string_char = cmd[index]
                        elif cmd[index] == '(':
                            parenthesis_depth += 1
                        elif cmd[index] == ')':
                            parenthesis_depth -= 1
                    try:
                        exec(argument_functions.valid_commands[real_cmd] + '\n\n' + cmd[:index + 1], globals())
                    except NameError:
                        exec(argument_functions.valid_commands[real_cmd] + '\n\n' + cmd[:cmd.find('(') + 1] + "'" + cmd[cmd.find('(') + 1:cmd.rfind(')')] + "'" + cmd[cmd.rfind(')'):index + 1], globals())
                    return_value = globals()['return_value']
                    if argument[:last_index] == '' and argument[last_index + len(function_prefix) + index + 1 + argument[last_index:].count(' '):] == '':
                        return return_value
                    else:
                        argument = argument[:last_index] + str(return_value) + argument[last_index + len(function_prefix + cmd[:index + 1]):]
                except IndexError:
                    return argument
        return argument


# Gathers file data.
def get_file_data(files=None):
    if files is None:
        try:
            with open('prefs.cfg', 'r') as r:
                prefs = json.load(r)
            directories = prefs['json directories']
        except (OSError, IOError, json.decoder.JSONDecodeError, KeyError):
            directories = ['..']
        files = []
        try:
            for directory in directories:
                files+= [os.path.join(directory, file) for file in os.listdir(directory)]
        except FileNotFoundError:
            pass
    file_data = {}
    for file in files:
        try:
            with open(file, 'r') as r:
                file_data[file] = json.load(r)
        except (OSError, IOError, json.decoder.JSONDecodeError):
            files.remove(file)
            file_data = get_file_data(files)
            break
    return file_data


# Parses arguments.
def parse_args(arguments, function_prefix):
    if arguments is None:
        return None
    if type(arguments) is list:
        for i in range(len(arguments)):
            arguments[i] = parse_args(arguments[i], function_prefix)
        return arguments
    elif type(arguments) is dict:
        for argument in arguments:
            arguments[argument] = parse_args(argument, function_prefix)
        return arguments
    elif type(arguments) is str:
        if not type(function_prefix) is str or not function_prefix:
            function_prefix = argument_functions.function_prefix
        return argument_functions.go_arg_commands(arguments, function_prefix)
    elif type(arguments) is tuple:
        return parse_args(list(arguments))
    else:
        return arguments


# Sees if the command is scheduled to run.
def scheduled_to_run(current_file):
    if not current_file:
        return False
    if 'run options' not in current_file:
        return True
    else:
        current_file
    can_run_based_on_time_interval = False
    last_run = None

    if 'random chance' in current_file['run options']:
        if random.random() >= current_file['run options']['random chance']:
            return False

    def test_numerical_instance(current, testee):
        try:
            if testee is None:
                return False
            if type(testee) is int:
                return current == testee
            elif type(testee) is str:
                testee = testee.replace(' ', '')
                if '-' in testee:
                    if testee.index('-') == 0:
                        return current <= int(testee[1:])
                    elif testee.index('-') == len(testee) - 1:
                        return current >= int(testee[:len(testee) - 1])
                    low = int(testee[:testee.index('-')])
                    high = int(testee[testee.index('-') + 1:])
                    if low <= high:
                        return low <= current <= high
                    return high >= current or low <= current
                elif testee == '*':
                    return True
                return current == int(testee)
            elif type(testee) is list:
                if len(testee) == 0:
                    return True
                for test in testee:
                    if test_numerical_instance(current, test):
                        return True
                return False
            return False
        except ValueError:
            return False

    if 'delay mode' in current_file['run options'] and current_file['run options']['delay mode'] and 'last run' in current_file:
        delay_mode = current_file['run options']['delay mode'].replace(' ', '').lower()
        if delay_mode == 'once':
            return False
        try:
            last_run = datetime.datetime(current_file['last run']['year'], current_file['last run']['month'],
                                         current_file['last run']['day'], current_file['last run']['hour'],
                                         current_file['last run']['minute'])
            if last_run > today:
                raise KeyError
            try:
                days_per_month = [31, 29 if isleap(last_run.year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                second_intervals = {'year': 86400 * (366 if isleap(last_run.year) else 365),
                                    'month': 86400 * days_per_month[last_run.month - 1], 'week': 604800, 'day': 86400,
                                    'hour': 3600, 'minute': 60}
                if 'lastmonthday' in delay_mode:
                    can_run_based_on_time_interval = today.day == days_per_month[today.month - 1]
                elif 'passed' in delay_mode:
                    for time_type in second_intervals:
                        if time_type in delay_mode:
                            try:
                                count = int(delay_mode[:delay_mode.find(time_type)])
                                second_intervals['month'] = 86400 * 30
                            except ValueError:
                                count = 1
                            if (today - last_run).total_seconds() > second_intervals[time_type] * count:
                                can_run_based_on_time_interval = True
                                break
                else:
                    time_passed_appropriate = {'yearly': last_run.year < today.year,
                                               'monthly': last_run.month < today.month or last_run.year < today.year,
                                               'weekly': last_run.isocalendar()[1] < today.isocalendar()[1] or (last_run.year < today.year and not (today.month == 1 and datetime.date(today.year, 1, 1).isocalendar()[2] != 1 and today.day < (9 - datetime.date(today.year, 1, 1).isocalendar()[2]))),
                                               "daily": last_run.day < today.day or last_run.month < today.month or last_run.year < today.year,
                                               "daily": last_run.day < today.day or last_run.month < today.month or last_run.year < today.year,
                                               "hourly": last_run.hour < today.hour or last_run.day < today.day or last_run.month < today.month or last_run.year < today.year}
                    for time_type in time_passed_appropriate:
                        if time_type in delay_mode:
                            can_run_based_on_time_interval = time_passed_appropriate[time_type]
                            break
            except TypeError:
                None
        except KeyError:
            None
    else:
        can_run_based_on_time_interval = True

    if not can_run_based_on_time_interval:
        return False
    can_run_based_on_current_datetime = True

    if 'year' in current_file['run options']:
        if not test_numerical_instance(today.year, current_file['run options']['year']):
            can_run_based_on_current_datetime = False

    def replace_month(replace_thing):
        months = [['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
                   'november', 'december'],
                  ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec']]
        if type(replace_thing) is str:
            for way in months:
                for month in range(len(way)):
                    if way[month] in replace_thing.lower():
                        replace_thing = replace_thing.lower().replace(way[month], str(month + 1))
        elif type(replace_thing) is list:
            for month in range(len(replace_thing)):
                if type(replace_thing[month]) is str:
                    for way in months:
                        for month in range(len(way)):
                            if way[month] in replace_thing[month].lower():
                                replace_thing[month] = replace_thing[month].lower().replace(way[month], str(month + 1))
        return replace_thing

    if 'month' in current_file['run options'] and can_run_based_on_current_datetime:
        if not test_numerical_instance(today.month, replace_month(current_file['run options']['month'])):
            can_run_based_on_current_datetime = False

    def replace_weekday(replace_thing):
        days = [['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                ['mon', 'tues', 'wednes', 'thurs', 'fri', 'sat', 'sun'],
                ['mon', 'tues', 'wednes', 'thur', 'fri', 'sat', 'sun'],
                ['mon', 'tues', 'wed', 'thu', 'fri', 'sat', 'sun'],
                ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su'],
                ['m', 't', 'w', 'h', 'f', 's', 'u']]
        if type(replace_thing) is str:
            for way in days:
                for day in range(len(way)):
                    if way[day] in replace_thing.lower():
                        replace_thing = replace_thing.lower().replace(way[day], str(day))
        elif type(replace_thing) is list:
            for weekday in range(len(replace_thing)):
                if type(replace_thing[weekday]) is str:
                    for way in days:
                        for day in range(len(way)):
                            if way[day] in replace_thing[weekday].lower():
                                replace_thing[weekday] = replace_thing[weekday].lower().replace(way[day], str(day))
        return replace_thing

    if 'weekday' in current_file['run options'] and can_run_based_on_current_datetime:
        if not test_numerical_instance(today.weekday(), replace_weekday(current_file['run options']['weekday'])):
            can_run_based_on_current_datetime = False
    if 'day' in current_file['run options'] and can_run_based_on_current_datetime:
        if not test_numerical_instance(today.day, current_file['run options']['day']):
            can_run_based_on_current_datetime = False
    if 'hour' in current_file['run options'] and can_run_based_on_current_datetime:
        if not test_numerical_instance(today.hour, current_file['run options']['hour']):
            can_run_based_on_current_datetime = False
    if 'minute' in current_file['run options'] and can_run_based_on_current_datetime:
        if not test_numerical_instance(today.minute, current_file['run options']['minute']):
            can_run_based_on_current_datetime = False

    if can_run_based_on_time_interval and not can_run_based_on_current_datetime and last_run and 'run if chance passed' in current_file['run options'] and current_file['run options']['run if chance passed']:
        valid_years = '*' if not 'year' in current_file['run options'] else current_file['run options']['year']
        valid_months = '*' if not 'month' in current_file['run options'] else replace_month(current_file['run options']['month'])
        valid_weekdays = '*' if not 'weekday' in current_file['run options'] else replace_weekday(current_file['run options']['weekday'])
        valid_days = '*' if not 'day' in current_file['run options'] else current_file['run options']['day']
        valid_hours = '*' if not 'hour' in current_file['run options'] else current_file['run options']['hour']
        valid_minutes = '*' if not 'minute' in current_file['run options'] else current_file['run options']['minute']
        for year in range(last_run.year, today.year + 1):
            if test_numerical_instance(year, valid_years):
                for month in range(last_run.month if year == last_run.year else 1,
                                   today.month + 1 if year == today.year else 13):
                    if test_numerical_instance(month, valid_months):
                        for day in range(last_run.day if year == last_run.year and month == last_run.month else 1, today.day + 1 if year == today.year and month == today.month else days_per_month[month - 1] + 1):
                            if test_numerical_instance(day, valid_days) and test_numerical_instance(datetime.date(year, month, day).isocalendar()[2] - 1, valid_weekdays):
                                for hour in range(last_run.hour if year == last_run.year and month == last_run.month and day == last_run.day else 0, today.hour + 1 if year == today.year and month == today.month and day == today.day else 24):
                                    if test_numerical_instance(hour, valid_hours):
                                        for minute in range(last_run.minute if year == last_run.year and month == last_run.month and day == last_run.day and hour == last_run.hour else 0, today.minute + 1 if year == today.year and month == today.month and day == today.day and hour == today.hour else 60):
                                            if test_numerical_instance(minute, valid_minutes):
                                                return True
        return False
    return can_run_based_on_current_datetime


# Writes to the file once it's done.
def write_to_json_file(current_file, file_data):
    def write_json_thing(file, thing, prior_spaces, final):
        if thing is None:
            file.write('null')
        elif type(thing) is bool:
            file.write('true' if thing else 'false')
        elif type(thing) is str:
            file.write('"' + thing.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"')
        elif type(thing) is int or type(thing) is float:
            file.write(str(thing))
        elif type(thing) is list:
            file.write('[\n')
            for val_index in range(len(thing)):
                file.write((prior_spaces + 4) * ' ')
                write_json_thing(file, thing[val_index], prior_spaces + 4, val_index == len(thing) - 1)
            file.write(prior_spaces * ' ' + ']')
        elif type(thing) is dict:
            file.write('{\n')
            keys = [key for key in thing.keys()]
            for val_index in range(len(keys)):
                file.write((prior_spaces + 4) * ' ' + '"' + keys[val_index] + '": ')
                write_json_thing(file, thing[keys[val_index]], prior_spaces + 4, val_index == len(thing) - 1)
            file.write(prior_spaces * ' ' + '}')
        elif type(thing) is tuple:
            file.write('[\n')
            for val_index in range(len(thing)):
                file.write((prior_spaces + 4) * ' ')
                write_json_thing(file, thing[val_index], prior_spaces + 4, val_index == len(thing) - 1)
            file.write(prior_spaces * ' ' + ']')
        if final:
            file.write('\n')
        else:
            file.write(',\n')

    with open(current_file, 'w') as file:
        file.write('{\n')
        keys = [key for key in file_data]
        if 'last run' in keys:
            keys.remove('last run')
        for value_index in range(len(keys)):
            file.write('    "' + keys[value_index] + '": ')
            write_json_thing(file, file_data[keys[value_index]], 4, False)
        file.write('    "last run": {\n')
        file.write('        "year": ' + str(today.year) + ',\n')
        file.write('        "month": ' + str(today.month) + ',\n')
        file.write('        "day": ' + str(today.day) + ',\n')
        file.write('        "hour": ' + str(today.hour) + ',\n')
        file.write('        "minute": ' + str(today.minute) + '\n')
        file.write('    }\n')
        file.write('}')
        file.close()


# Main part of the program right here.
if __name__ == '__main__':
    directory = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    valid_commands = {'sleep': general.sleep,
                      'conditional end': general.conditional_end,
                      'conditional skip': general.conditional_skip,
                      'conditional switch': general.conditional_switch,
                      'create backup': files.create_backup,
                      'copy file': files.copy_file,
                      'append file': files.append_file,
                      'overwrite file': files.overwrite_file,
                      'delete file': files.delete_file,
                      'kill process': processes.kill_process,
                      'suspend process': processes.suspend_process,
                      'resume process': processes.resume_process,
                      'open webpage': webpages.open_webpage,
                      'simulate keyboard': hardware.simulate_keyboard,
                      'simulate mouse': hardware.simulate_mouse,
                      'command prompt': misc.command_prompt,
                      'popup': misc.popup,
                      'log': misc.log,
                      'do nothing': misc.do_nothing}
    last_minute = -1

    while True:
        today = datetime.datetime.today()
        current_minute = today.minute
        if current_minute == last_minute:
            time.sleep(6)
            continue
        gc.collect()
        file_data = get_file_data()
        for file in file_data:
            current_file = file_data[file]
            try:
                commands = current_file['command']
                args = None
                if 'args' in current_file:
                        args = current_file['args']
                if not scheduled_to_run(current_file):
                    continue
                output_file = file + '.output.txt'
                if 'output file' in current_file:
                    output_file = current_file['output file']
                if 'repeats' in current_file:
                    try:
                        repeats = int(current_file['repeats'])
                    except ValueError:
                        repeats = 0
                else:
                    repeats = 0
                if type(commands) is list:
                    command_runner([(valid_commands[command.lower().replace('_', ' ')] if command.lower().replace('_', ' ') in valid_commands else command.lower().replace('_', ' ')) if type(command) is str else str(command) for command in commands], args, file, output_file, current_file['args function prefix'] if 'args function prefix' in current_file else argument_functions.function_prefix, repeats)
                    write_to_json_file(file, current_file)
                else:
                    command_runner(valid_commands[commands.lower().replace('_', ' ')] if commands.lower().replace('_', ' ') in valid_commands else commands.lower().replace('_', ' '), args, file, output_file, current_file['args function prefix'] if 'args function prefix' in current_file else argument_functions.function_prefix, repeats)
                    write_to_json_file(file, current_file)
            except (KeyError, TypeError):
                continue
        last_minute = current_minute
