import os
import pyautogui

from jadmain import output


def command_prompt(file, filename, args):
    if type(args) is list:
        for arg in args:
            reply = os.popen(str(arg)).read()
            while reply.endswith('\n'):
                reply = reply[:len(reply) - 1]
            output('command prompt: ' + str(arg) + ': ' + reply, filename, file)
    else:
        reply = os.popen(str(args)).read()
        while reply.endswith('\n'):
            reply = reply[:len(reply) - 1]
        output('command prompt: ' + str(args) + ': ' + reply, filename, file)


def popup(file, filename, args):
    if type(args) is list:
        if len(args) >= 3:
            pyautogui.alert(str(args[0]), str(args[1]), str(args[2]))
        elif len(args) == 2:
            pyautogui.alert(str(args[0]), str(args[1]))
        elif len(args) == 1:
            pyautogui.alert(str(args[0]))
        else:
            pyautogui.alert(str(args))
    elif args != None:
        pyautogui.alert(str(args))
    else:
        pyautogui.alert()


def log(file, filename, args):
    if type(args) is list:
        for thing in args:
            log(file, filename, str(args))
    else:
        output('log: {}'.format(str(args)), filename, file)


def do_nothing(file, filename, args):
    output('do_nothing: Doing nothing.', filename, file)
    return