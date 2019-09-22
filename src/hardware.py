import pyautogui
from ast import literal_eval

from jadmain import output

def simulate_mouse(file, filename, args):
    method = '''if True:
            def setpos(x, y):
                pyautogui.moveTo(x, y)
            def move(x, y):
                pyautogui.move(x, y)
            def click(button, amount=1):
                mouse_buttons = ['left', 'right', 'middle']
                for i in range(amount):
                    pyautogui.click(button=mouse_buttons[button % 3])
            def press(button):
                mouse_buttons = ['left', 'right', 'middle']
                pyautogui.mouseDown(button=mouse_buttons[button % 3])
            def release(button):
                mouse_buttons = ['left', 'right', 'middle']
                pyautogui.mouseUp(button=mouse_buttons[button % 3])
            def scroll(dx, dy = ""):
                if type(dy) is str:
                    pyautogui.scroll(dx)
                else:
                    pyautogui.scroll(dy)
                    pyautogui.hscroll(dx)
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
            method += cmd[:cmd.rfind(')') + 1] + '\n'
        exec(method)


def simulate_keyboard(file, filename, args):
    standard_keys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']
    shifted_keys = {'~': '`', '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0', '_': '-', '+': '=', ':': ';', '"': "'", '<': ',', '>': '.', "?": '/'}
    sub_keys = {'alt': 'alt',
                'lalt': 'altleft',
                'altleft': 'altleft',
                'ralt': 'altright',
                'altright': 'altright',
                'backspace': 'backspace',
                'capslock': 'capslock',
                'caps': 'capslock',
                'control': 'ctrl',
                'ctrl': 'ctrl',
                'lcrtl': 'ctrlleft',
                'ctrlleft': 'ctrlleft',
                'ctrlright': 'ctrlright',
                'delete': 'del',
                'del': 'del',
                'down': 'down',
                'end': 'end',
                'enter': 'enter',
                'return': 'enter',
                'esc': 'esc',
                'f1': 'f1',
                'f2': 'f2',
                'f3': 'f3',
                'f4': 'f4',
                'f5': 'f5',
                'f6': 'f6',
                'f7': 'f7',
                'f8': 'f8',
                'f9': 'f9',
                'f10': 'f10',
                'f11': 'f11',
                'f12': 'f12',
                'f13': 'f13',
                'f14': 'f14',
                'f15': 'f15',
                'f16': 'f16',
                'f17': 'f17',
                'f18': 'f18',
                'f19': 'f19',
                'f20': 'f20',
                'home': 'home',
                'insert': 'insert',
                'ins': 'insert',
                'left': 'left',
                'menu': 'home',
                'numlock': 'numlock',
                'num0': 'num0',
                'num1': 'num1',
                'num2': 'num2',
                'num3': 'num3',
                'num4': 'num4',
                'num5': 'num5',
                'num6': 'num6',
                'num7': 'num7',
                'num8': 'num8',
                'num9': 'num9',
                'pagedown': 'pagedown',
                'pgdown': 'pagedown',
                'pgdn': 'pagedown',
                'pageup': 'pageup',
                'pgup': 'pageup',
                'pause': 'pause',
                'break': 'pause',
                'printscreen': 'printscreen',
                'prntscrn': 'printscreen',
                'prtscr': 'printscreen',
                'right': 'right',
                'scrolllock': 'scrolllock',
                'scrlock': 'scrolllock',
                'shift': 'shift',
                'lshift': 'shiftleft',
                'shifteft': 'shiftleft',
                'rshift': 'shiftright',
                'shiftright': 'shiftright',
                'space': 'space',
                'spc': 'space',
                'tab': 'tab',
                'up': 'up',
                'windows': 'win',
                'win': 'win',
                'lwindows': 'winleft',
                'lwin': 'winleft',
                'rwindows': 'winright',
                'rwin': 'winright'}

    def ktype(message):
        pyautogui.typewrite(message)

    def click(key):
        key = key.replace(' ', '').lower()
        if key in shifted_keys:
            key = shifted_keys[key]
        elif key in sub_keys:
            key = sub_keys[key]
        pyautogui.keyDown(key)
        pyautogui.keyUp(key)

    def press(key):
        key = key.replace(' ', '').lower()
        if key in shifted_keys:
            key = shifted_keys[key]
        elif key in sub_keys:
            key = sub_keys[key]
        pyautogui.keyDown(key)

    def release(key):
        key = key.replace(' ', '').lower()
        if key in shifted_keys:
            key = shifted_keys[key]
        elif key in sub_keys:
            key = sub_keys[key]
        pyautogui.keyUp(key)

    def stroke(sequence):
        keys = []
        now_start_at = 0
        if '+' in sequence:
            sequence = sequence.replace(' ', '').lower()
            for i in range(sequence.count('+')):
                end_index = sequence.find('+', now_start_at)
                key = sequence[now_start_at:end_index]
                if key in shifted_keys:
                    key = shifted_keys[key]
                elif key in sub_keys:
                    key = sub_keys[key]
                keys.append(key)
                now_start_at = end_index + 1
            key = sequence[now_start_at:]
            if key in shifted_keys:
                key = shifted_keys[key]
            elif key in sub_keys:
                key = sub_keys[key]
            now_start_at = end_index + 1
            keys.append(key)
        else:
            sequence = sequence.replace(' ', '').lower()
            if sequence in shifted_keys:
                sequence = shifted_keys[sequence]
            elif sequence in sub_keys:
                sequence = sub_keys[sequence]
            keys.append(sequence)
        for keyz in keys:
            pyautogui.keyDown(keyz)
        for keyz in keys:
            pyautogui.keyUp(keyz)

    def test_message(arguments):
        return ktype

    def test_click(arguments):
        arguments = arguments.replace(' ', '').lower()
        if arguments in standard_keys or arguments in shifted_keys or arguments in sub_keys:
            return click
        return '"{}" is not a valid key!'.format(arguments)

    def test_press(arguments):
        arguments = arguments.replace(' ', '').lower()
        if arguments in standard_keys or arguments in shifted_keys or arguments in sub_keys:
            return press
        return '"{}" is not a valid key!'.format(arguments)

    def test_release(arguments):
        arguments = arguments.replace(' ', '').lower()
        if arguments in standard_keys or arguments in shifted_keys or arguments in sub_keys:
            return release
        return '"{}" is not a valid key!'.format(arguments)

    def test_keystroke(arguments):
        arguments = arguments.replace(' ', '').lower()
        if '+' in arguments:
            now_start_at = 0
            for i in range(arguments.count('+')):
                end_index = arguments.find('+', now_start_at)
                key = arguments[now_start_at:end_index]
                if not (key in standard_keys or key in shifted_keys or key in sub_keys):
                    return '"{}" is not a valid keystroke!'.format(arguments)
                now_start_at = end_index + 1
            key = arguments[now_start_at:]
            if not (key in standard_keys or key in shifted_keys or key in sub_keys):
                return '"{}" is not a valid keystroke!'.format(arguments)
            return stroke
        else:
            if arguments in standard_keys or arguments in shifted_keys or arguments in sub_keys:
                return stroke
        return '"{}" is not a valid keystroke!'.format(arguments)

    valid_methods = {'type': test_message, 'click': test_click, 'press': test_press, 'release': test_release, 'stroke': test_keystroke}

    if not args or not (type(args) is list or type(args) is str):
        return output('simulate keyboard: Args is invalid! Must be a string or a list of strings!', filename, file)
    elif type(args) is str:
        if not ('(' in args and ')' in args):
            return output('simulate keyboard: Argument {} is invalid! Missing parhenthesis!'.format(args), filename, file)
        params = args[args.find('(') + 1: args.rfind(')')]
        if ((params[0] == '"' and params[len(params) - 1] == '"') or (params[0] == "'" and params[len(params) - 1] == "'")) and len(params) > 1:
            params = params[1:len(params) - 1]
        method_name = args[:args.find('(')].lower()
        if method_name in valid_methods:
            command = valid_methods[method_name](params)
        else:
            return output('simulate keyboard: Argument {} is invalid! {} is not a valid method name!'.format(args, method_name), filename, file)
        if command and type(command) is str:
            return output('simulate keyboard: Argument {} is invalid! '.format(args) + command, filename, file)
        elif command:
            command(params)
        else:
            return output('simulate keyboard: Some unknown error occurred.', filename, file)
    else:
        commands = []
        for cmd in args:
            command = None
            if type(cmd) is str:
                if not ('(' in cmd and ')' in cmd):
                    return output('simulate keyboard: Argument {} is invalid! Missing parhenthesis!'.format(cmd), filename, file)
                params = cmd[cmd.find('(') + 1: cmd.rfind(')')]
                if ((params[0] == '"' and params[len(params) - 1] == '"') or (params[0] == "'" and params[len(params) - 1] == "'")) and len(params) > 1:
                    params = params[1:len(params) - 1]
                method_name = cmd[:cmd.find('(')].lower()
                if method_name in valid_methods:
                    command = valid_methods[method_name](params)
                else:
                    return output('simulate keyboard: Argument {} is invalid! {} is not a valid method name!'.format(cmd, method_name), filename, file)
                if command and type(command) is str:
                    return output('simulate keyboard: Argument {} is invalid! '.format(cmd) + command, filename, file)
                elif command:
                    commands.append([command, params])
                else:
                    return output('simulate keyboard: Some unknown error occurred.', filename, file)
            else:
                return output('simulate keyboard: Argument {} is invalid! Must be a string!'.format(cmd), filename, file)
        for cmd in commands:
            cmd[0](cmd[1])