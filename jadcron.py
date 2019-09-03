import gc
import os
import json
import time
import random
import shutil
import datetime
import pynput.mouse as mouse
from calendar import isleap
from ast import literal_eval
from threading import Thread

AUTHOR = 'Jade Godwin'
VERSION = '0.2.1'

DEBUG = False

today = None


# Handles console logging and file output.
def output(text, file, output_file=None):
    if output_file:
        output_file.write('{}\n'.format(text))
    if text != '\n':
        print(os.path.basename(file) + ': ' + text)
    else:
        print()


# Actually runs the command iteself.
class command_runner(Thread):
    def __init__(self, commands, args, filename, output_file):
        Thread.__init__(self)
        self.commands = commands
        self.args = args
        self.filename = filename
        self.file = None
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
            if self.args is None or (not type(self.args) is list and not len(self.args) == len(self.commands)):
                output('Args needs to be an array of equal length to the command array!', self.filename, self.file)
            else:
                for command in range(len(self.commands)):
                    if type(self.commands[command]) is str:
                        output('{} is not a valid command.'.format(self.commands[command]), self.filename, self.file)
                    else:
                        output('Running command {} with arguments {}.'.format(self.commands[command].__name__, self.args[command]), self.filename, self.file)
                        self.commands[command](self.file, self.filename, self.args[command])
                        output('', self.filename, self.file)
        else:
            if type(self.commands) is str:
                output('{} is not a valid command.'.format(self.commands), self.filename, self.file)
            else:
                output('Running command {} with arguments {}.'.format(self.commands.__name__, ('"' + str(self.args) + '"') if type(self.args) is str else self.args), self.filename, self.file)
                self.commands(self.file, self.filename, self.args)
        output('\n', self.filename, self.file)
        if self.file:
            self.file.close()


# File operations.
class file_operations():

    @staticmethod
    def copy_file(file, filename, args):

        def do_the_copy_thing(src, dst, keep_attributes=True):
            if not type(src) is str:
                output('copy file: Source file {} is not a string! Cannot copy file.'.format(str(src)), filename, file)
                return
            if not os.path.isfile(src):
                output('copy file: Source file {} does not exist! Cannot copy file.'.format(str(src)), filename, file)
                return
            if type(dst) is list:
                for dest in dst:
                    do_the_copy_thing(src, dest, keep_attributes)
            if not type(dst) is str:
                output('copy file: Destination file/folder {} is not a string! Cannot copy files'.format(str(dst)),
                       filename, file)
                return 0
            if os.path.isdir(dst) and os.path.normpath(os.path.dirname(src)) == os.path.normpath(dst):
                output(
                    'copy file: Source file {} is already in the destination folder! Copying would be redundant.'.format(
                        src), filename, file)
            if os.path.normpath(src) == os.path.normpath(dst):
                output(
                    'copy file: Source file and destination file are the same ({})! Copying would be redundant.'.format(
                        os.path.normpath(dst)), filename, file)
            src = os.path.normpath(src)
            dst = os.path.normpath(dst)
            copy = shutil.copy2 if keep_attributes else shutil.copy
            try:
                if not os.path.exists(dst):
                    dest = dst
                    if '.' in os.path.basename(dst):
                        dest = os.path.dirname(dst)
                    while not (os.path.isdir(dest) or os.path.dest == ''):
                        try:
                            os.mkdir(dest)
                        except FileNotFoundError:
                            dst_temp = os.path.dirname(dest)
                            while not (os.path.isdir(dst_temp) or dst_temp == ''):
                                try:
                                    os.mkdir(dst_temp)
                                except FileNotFoundError:
                                    dst_temp = os.path.dirname(dst_temp)
                copy(src, dst)
                output('copy file: Copied {} to {}.'.format(src, dst), filename, file)
            except PermissionError:
                output('copy file: Got permission error while copying from {} to {}!'.format(src, dst), filename, file)
                return 0

        if not args:
            return output('copy file: Command cannot run without arguments!', filename, file)
        if not type(args) is list or len(args) < 2:
            return output('copy file: Args is invalid! Must be a list of at least length 2!', filename, file)
        elif len(args) > 2:
            do_the_copy_thing(args[0], args[1], args[2])
        else:
            do_the_copy_thing(args[0], args[1])

    @staticmethod
    def create_backup(file, filename, args):

        def do_the_copy_thing(src, dst, detailed_output=False, keep_attributes=True):
            # Recursive call if list
            if type(src) is list:
                files_copied = 0
                for source in src:
                    if os.path.isdir(source):
                        files_copied += do_the_copy_thing(source, os.path.join(dst, os.path.basename(source)),
                                                          detailed_output, keep_attributes)
                    else:
                        files_copied += do_the_copy_thing(source, dst, detailed_output, keep_attributes)
                return files_copied
            if not type(src) is str:
                output('create backup: Source file/folder {} is not a string! Cannot copy files.'.format(str(src)), filename, file)
                return 0
            if not os.path.exists(src):
                output('create backup: Source file/folder {} does not exist! Cannot copy files.'.format(src), filename, file)
                return 0
            if type(dst) is list:
                files_copied = 0
                for dest in dst:
                    files_copied += do_the_copy_thing(src, dest, keep_attributes)
                return files_copied
            # Handle user error
            if not type(dst) is str:
                output('create backup: Destination folder {} is not a string! Cannot copy files'.format(str(dst)),
                       filename, file)
                return 0
            if os.path.isfile(dst):
                output(
                    'create backup: Destination {} is a file, not a folder! Use the command copy file to copy files.'.format(str(dst)), filename, file)
                return 0
            src = os.path.normpath(src)
            dst = os.path.normpath(dst)
            if (os.path.isdir(src) and src == dst) or (os.path.isfile(src) and os.path.dirname(src) == dst):
                output('create backup: Source folder and destination folder are one and the same! Copying files would be redundant.', filename, file)
            # Set copy command
            copy = shutil.copy2 if keep_attributes else shutil.copy
            # Make destination folder
            try:
                while not (os.path.isdir(dst) or dst == ''):
                    try:
                        os.mkdir(dst)
                    except FileNotFoundError:
                        dst_temp = os.path.dirname(dst)
                        while not (os.path.isdir(dst_temp) or dst_temp == ''):
                            try:
                                os.mkdir(dst_temp)
                            except FileNotFoundError:
                                dst_temp = os.path.dirname(dst_temp)
                if os.path.isfile(src):
                    copy(src, dst)
                else:
                    def handle_save_dir(file_folder):
                        if file_folder == dst:
                            return 0
                        if os.path.isdir(file_folder):
                            try:
                                os.mkdir(os.path.join(dst, os.path.relpath(file_folder, src)))
                            except FileExistsError:
                                None
                            files_copied = 0
                            for sub_file_folder in os.listdir(file_folder):
                                files_copied += handle_save_dir(
                                    os.path.normpath(os.path.join(file_folder, sub_file_folder)))
                            return files_copied
                        else:
                            destination_file = os.path.join(dst, os.path.dirname(os.path.relpath(file_folder, src)))
                            copy(file_folder, destination_file)
                            if detailed_output:
                                output('create backup: Copied {} to {}.'.format(file_folder, destination_file), filename, file)
                            return 1
                    files_copied = 0
                    for file_folder in os.listdir(src):
                        files_copied += handle_save_dir(os.path.normpath(os.path.join(src, file_folder)))
                    return files_copied
            except PermissionError:
                output('create backup: Got permission error while copying from {} to {}!'.format(src, dst), filename, file)
                return 0

        if not args:
            return output('create backup: Command cannot run without arguments!', filename, file)
        if not type(args) is list or len(args) < 2:
            return output('create backup: Args is invalid! Must be a list of at least length 2!', filename, file)
        if len(args) > 3:
            files_copied = do_the_copy_thing(args[0], args[1], args[2], args[3])
        elif len(args) > 2:
            files_copied = do_the_copy_thing(args[0], args[1], args[2])
        else:
            files_copied = do_the_copy_thing(args[0], args[1])
        output('create backup: {} total files copied from {} to {}.'.format(files_copied, args[0], args[1]), filename, file)

    @staticmethod
    def append_file(file, filename, args, overwrite = False):

        def do_the_writey_thing(filz, writing, detailed_output=False):
            if type(filz) is list:
                files_written = 0
                for filzz in filz:
                    files_written+= do_the_writey_thing(filzz, writing)
                return files_written
            if not type(filz) is str:
                output('{}: File {} is not a string! Cannot write to file.'.format('overwrite file' if overwrite else 'append file', str(filz)), filename, file)
                return 0
            filz = os.path.normpath(filz)
            try:
                while not (os.path.isdir(os.path.dirname(filz)) or os.path.dirname(filz) == ''):
                    try:
                        os.mkdir(os.path.dirname(filz))
                    except FileNotFoundError:
                        dst_temp = os.path.dirname(filz)
                        while not (os.path.isdir(dst_temp) or dst_temp == ''):
                            try:
                                os.mkdir(dst_temp)
                            except FileNotFoundError:
                                dst_temp = os.path.dirname(dst_temp)
                with open(filz, 'w' if overwrite else 'a') as writ:
                    if type(writing) is list:
                        for i in range(len(writing)):
                            writ.write(str(writing[i]))
                    else:
                        writ.write(writing)
                output('{}: Successfully wrote to file {}.'.format('overwrite file' if overwrite else 'append file', filz), filename, file)
                return 1
            except PermissionError:
                output('{}: Got permission error while trying to write to file {}!'.format('overwrite file' if overwrite else 'append file', filz), filename, file)
                return 0

        if not args:
            return output('{}: Command cannot run without arguments!'.format('overwrite file' if overwrite else 'append file'), filename, file)
        if not type(args) is list or len(args) < 2:
            return output('{}: Args is invalid! Must be a list of at least length 2!'.format('overwrite file' if overwrite else 'append file'), filename, file)
        files_written = do_the_writey_thing(args[0], args[1:])
        if files_written <= 0:
            return output('{}: Wrote to no files.'.format('overwrite file' if overwrite else 'append file'), filename, file)
        elif files_written > 1:
            return output('{}: Wrote to {} files.'.format('overwrite file' if overwrite else 'append file', files_written), filename, file)

    @staticmethod
    def overwrite_file(file, filename, args):
        file_operations.append_file(file, filename, args, True)

    @staticmethod
    def delete_file(file, filename, args):

        def do_deletion(thing, ignore_output = False):
            if type(thing) is list:
                for dir in thing:
                    do_deletion(dir)
                return
            thing = os.path.normpath(thing)
            try:
                if not os.path.exists(thing) and not ignore_output:
                    return output('delete file: File or folder {} does not exist. No deletion done.'.format(thing), filename, file)
                if os.path.isdir(thing):
                    shutil.rmtree(thing)
                    output('delete file: Deleted folder {}.'.format(thing), filename, file)
                else:
                    os.remove(thing)
                    output('delete file: Deleted file {}.'.format(thing), filename, file)
            except PermissionError:
                output('delete file: Got permission error while deleting {}!'.format(thing), filename, file)

        if not args or not(type(args) is list or type(args) is str):
            return output('delete file: Args is invalid! Must be a string or a list containing at least one string!', filename, file)
        do_deletion(args)


# Opens a webpage.
class open_webpage():
    valid_ints = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    @staticmethod
    def run(file, filename, args):

        def do_open_page(site):
            if not type(site) is str:
                if type(site) is list:
                    for sitez in site:
                        do_open_page(sitez)
                return output('open webpage: {} is not a string and thus cannot be a valid URL!'.format(site), filename,
                              file)
            else:
                if not (args.startswith('http://') or args.startswith('https://') or args.startswith('localhost:') or
                        site[0] in open_webpage.valid_ints):
                    output(
                        'open webpage: Webpage {} does not start with http://, hhtps://, localhost:, or a number. Adding http:// to the beginning of the URL.',
                        filename, file)
                    site = 'http://' + site
            os.system('start \"\" ' + site)
            output('open webpage: Webpage ' + args + ' opened.', filename, file)

        if not args:
            return output('open webpage: Command cannot run without arguments!', filename, file)
        do_open_page(args)


# Hardware simulation.
class hardware_simulation():

    @staticmethod
    def simulate_mouse(file, filename, args):
        method = '''if True:
        def setpos(x, y):
            mouse_c = mouse.Controller()
            mouse_c.position = (x, y)
        def move(x, y):
            mouse_c = mouse.Controller()
            mouse_c.move(x, y)
        def click(button, amount=1):
            mouse_c = mouse.Controller()
            mouse_buttons = [mouse.Button.left, mouse.Button.right, mouse.Button.middle]
            mouse_c.click(mouse_buttons[button % 3], amount)
        def press(button):
            mouse_c = mouse.Controller()
            mouse_buttons = [mouse.Button.left, mouse.Button.right, mouse.Button.middle]
            mouse_c.press(mouse_buttons[button % 3])
        def release(button):
            mouse_c = mouse.Controller()
            mouse_buttons = [mouse.Button.left, mouse.Button.right, mouse.Button.middle]
            mouse_c.release(mouse_buttons[button % 3])
        def scroll(dx, dy = ""):
            mouse_c = mouse.Controller()
            if type(dy) is str:
                mouse_c.scroll(0, dx)
            else:
                mouse_c.scroll(dx, dy)
        \n'''

        def command_is_valid(argument):
            if not ('(' in argument and ')' in argument):
                return 'Argument {} is invalid! Missing parhenthesis!'.format(argument)
            method_name = argument[:argument.find('(')].lower()
            arguments = '[' + argument[argument.find('(') + 1: argument.rfind(')')] + ']'
            valid_methods = {'setpos': [2],
                             'move': [2],
                             'click': [2, 1],
                             'press': [1],
                             'release': [1],
                             'scroll': [1, 2]
            }
            if method_name in valid_methods:
                try:
                    arguments = literal_eval(arguments)
                    for arg in arguments:
                        if not type(arg) is int:
                            return 'Argument {} is invalid! Not all arguments are ints!'.format(argument)
                    if len(arguments) in valid_methods[method_name]:
                        return True
                    return 'Argument {} is invalid! Inappropriate amount of arguments!'.format(argument)
                except SyntaxError:
                    return 'Argument {} is invalid! Arguments are not formatted correctly!'.format(argument)
            else:
                return 'Argument {} is invalid! {} is not a valid method name!'.format(argument, method_name)

        if not args or not (type(args) is list or type(args) is str):
            return output('simulate mouse: Args is invalid! Must be a string or a list of strings!', filename, file)
        elif type(args) is str:
            command = command_is_valid(args)
            if command and type(command) is str:
                return output('simulate mouse: ' + command, filename, file)
            elif command:
                exec(method + args[:args.rfind(')') + 1])
            else:
                return output('simulate mouse: Some unknown error occurred.', filename, file)
        else:
            commands = []
            for cmd in args:
                command = None
                if type(cmd) is str:
                    command = command_is_valid(cmd)
                    if command and type(command) is str:
                        return output('simulate mouse: ' + command, filename, file)
                    elif command:
                        commands.append(cmd)
                    else:
                        return output('simulate mouse: Some unknown error occurred.', filename, file)
                else:
                    return output('simulate mouse: Argument {} is invalid! Must be a string!'.format(cmd), filename, file)
            for cmd in commands:
                method+= cmd[:cmd.rfind(')') + 1] + '\n'
            exec(method)


# Miscellaneous commands.
class misc_commands():

    @staticmethod
    def sleep(file, filename, args):
        if not args:
            return output('sleep: Command cannot run without arguments!', filename, file)
        if type(args) is int or type(args) is float:
            time.sleep(args)
            output('sleep: Slept for {} seconds.'.format(args), filename, file)
        elif file:
            output('sleep: Could not sleep as the argument {} was not a valid number!'.format(args), filename, file)
        return

    @staticmethod
    def do_nothing(file, filename, args):
        output('do_nothing: Doing nothing.', filename, file)
        return


# Gathers file data.
def get_file_data(files=None):
    if files is None:
        files = [os.path.join(directory, file) for file in os.listdir(directory) if
                 not (file.endswith('.py') or file.endswith('.bat') or file.endswith('.log') or file.endswith('.md'))]
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
                        ['M', 'T', 'W', 'H', 'F', 'S', 'U']]
                globals()['return_value'] = days[(style - 1) % 6][weekday]''',

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
                globals()['return_value'] = eval(thing)'''
    }

    @staticmethod
    def go_arg_commands(argument, function_prefix):
        if function_prefix in argument:
            last_index = len(argument)
            while argument.rfind(function_prefix, 0, last_index) != -1:
                last_index = argument.rfind(function_prefix, 0, last_index)
                cmd = argument[last_index:].replace(' ', '').replace(function_prefix, '')
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
                    exec(argument_functions.valid_commands[real_cmd] + '\n\n' + cmd[:index + 1], globals())
                    return_value = globals()['return_value']
                    if argument[:last_index] == '' and argument[
                                                       last_index + len(function_prefix) + index + 1 + argument[
                                                                                                       last_index:].count(
                                                               ' '):] == '':
                        return return_value
                    else:
                        argument = argument[:last_index] + str(return_value) + argument[last_index + len(
                            function_prefix + cmd[:index + 1]):]
                except IndexError:
                    None
        return argument


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
            if not testee:
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

    if 'delay mode' in current_file['run options'] and current_file['run options'][
        'delay mode'] and 'last run' in current_file:
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
                                               'weekly': last_run.isocalendar()[1] < today.isocalendar()[1] or (
                                                           last_run.year < today.year and not (today.month == 1 and
                                                                                               datetime.date(today.year,
                                                                                                             1,
                                                                                                             1).isocalendar()[
                                                                                                   2] != 1 and today.day < (
                                                                                                           9 -
                                                                                                           datetime.date(
                                                                                                               today.year,
                                                                                                               1,
                                                                                                               1).isocalendar()[
                                                                                                               2]))),
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

    if can_run_based_on_time_interval and not can_run_based_on_current_datetime and last_run and 'run if chance passed' in \
            current_file['run options'] and current_file['run options']['run if chance passed']:
        valid_years = '*' if not 'year' in current_file['run options'] else current_file['run options']['year']
        valid_months = '*' if not 'month' in current_file['run options'] else replace_month(
            current_file['run options']['month'])
        valid_weekdays = '*' if not 'weekday' in current_file['run options'] else replace_weekday(
            current_file['run options']['weekday'])
        valid_days = '*' if not 'day' in current_file['run options'] else current_file['run options']['day']
        valid_hours = '*' if not 'hour' in current_file['run options'] else current_file['run options']['hour']
        valid_minutes = '*' if not 'minute' in current_file['run options'] else current_file['run options']['minute']
        for year in range(last_run.year, today.year + 1):
            if test_numerical_instance(year, valid_years):
                for month in range(last_run.month if year == last_run.year else 1,
                                   today.month + 1 if year == today.year else 13):
                    if test_numerical_instance(month, valid_months):
                        for day in range(last_run.day if year == last_run.year and month == last_run.month else 1,
                                         today.day + 1 if year == today.year and month == today.month else
                                         days_per_month[month - 1] + 1):
                            if test_numerical_instance(day, valid_days) and test_numerical_instance(
                                    datetime.date(year, month, day).isocalendar()[2] - 1, valid_weekdays):
                                for hour in range(
                                        last_run.hour if year == last_run.year and month == last_run.month and day == last_run.day else 0,
                                        today.hour + 1 if year == today.year and month == today.month and day == today.day else 24):
                                    if test_numerical_instance(hour, valid_hours):
                                        for minute in range(
                                                last_run.minute if year == last_run.year and month == last_run.month and day == last_run.day and hour == last_run.hour else 0,
                                                today.minute + 1 if year == today.year and month == today.month and day == today.day and hour == today.hour else 60):
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
    valid_commands = {'copy file': file_operations.copy_file,
                      'create backup': file_operations.create_backup,
                      'append file': file_operations.append_file,
                      'overwrite file': file_operations.overwrite_file,
                      'delete file': file_operations.delete_file,
                      'open webpage': open_webpage.run,
                      'simulate mouse': hardware_simulation.simulate_mouse,
                      'sleep': misc_commands.sleep,
                      'do nothing': misc_commands.do_nothing}
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
                    if type(current_file['args']) is list or type(current_file['args']) is dict:
                        args = current_file['args'].copy()
                    else:
                        args = current_file['args']
                    args = parse_args(args, current_file['args function prefix'] if 'args function prefix' in current_file else argument_functions.function_prefix)
                if not scheduled_to_run(current_file):
                    continue
                output_file = file + '.output.txt'
                if 'output file' in current_file:
                    output_file = current_file['output file']
                if type(commands) is list:
                    command_runner([(valid_commands[command.lower().replace('_', ' ')] if command.lower().replace('_',
                                                                                                                  ' ') in valid_commands else command.lower().replace(
                        '_', ' ')) if type(command) is str else str(command) for command in commands], args, file,
                                   output_file)
                    write_to_json_file(file, current_file)
                else:
                    command_runner(valid_commands[commands.lower().replace('_', ' ')] if commands.lower().replace('_',
                                                                                                                  ' ') in valid_commands else commands.lower().replace(
                        '_', ' '), args, file, output_file)
                    write_to_json_file(file, current_file)
            except (KeyError, TypeError):
                continue
        last_minute = current_minute