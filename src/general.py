import time

from jadmain import output


def sleep(file, filename, args):
    if not args:
        return output('sleep: Command cannot run without arguments!', filename, file)
    if type(args) is int or type(args) is float:
        time.sleep(args)
        output('sleep: Slept for {} seconds.'.format(args), filename, file)
    elif file:
        output('sleep: Could not sleep as the argument {} was not a valid number!'.format(args), filename, file)
    return


def conditional_end(file, filename, args):
    if args:
        output('conditional end: {} is equivalent to True! Ending the program:'.format(args), filename, file)
        return -1, 0
    else:
        output('conditional end: {} is equivalent to False. Continuing as normal.'.format(args), filename, file)
        return 0, 0


def conditional_skip(file, filename, args):
    if not type(args) is list or len(args) != 2:
        output('conditional skip: Args is invalid! Must be a list of length 2!', filename, file)
        return 0, 0
    if not type(args[1]) is int:
        output('conditional skip: Args is invalid! The second value of the list needs to be an integer!', filename, file)
        return 0, 0
    if args[0]:
        output('conditional skip: {} is equivalent to True! Skipping {} commands:'.format(args[0], args[1]), filename, file)
        return args[1], 0
    else:
        output('conditional skip: {} is equivalent to False. Continuing as normal.'.format(args[0]), filename, file)
        return 0, 0


def conditional_switch(file, filename, args):
    if not type(args) is list or (len(args) > 3 or len(args) < 2):
        output('conditional switch: Args is invalid! Must be a list of length 3!', filename, file)
        return 0, 0
    if len(args) < 3:
        args = args.copy().append(0)
    if not type(args[1]) is int:
        output('conditional switch: Args is invalid! The second value of the list needs to be an integer!', filename, file)
        return 0, 0
    if len(args) == 3 and not type(args[2]) is int:
        output('conditional switch: Args is invalid! The third value of the list needs to be an integer!', filename, file)
        return 0, 0
    if args[0]:
        output('conditional switch: {} is equivalent to True! Doing {} commands then skipping {}.'.format(args[0], args[1], args[2]), filename, file)
        return args[2], args[1]
    else:
        output('conditional switch: {} is equivalent to False. Skipping {} commands.'.format(args[0], args[1]), filename, file)
        return args[1], 0
