import psutil

from jadmain import output

def get_processes(args):
    matching_processes = []
    try:
        args = int(args)
    except ValueError:
        args = str(args)
    for proc in psutil.process_iter():
        try:
            if type(args) is int:
                if args == proc.pid:
                    matching_processes.append(proc)
            else:
                if args.lower() in proc.name().lower():
                    matching_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied, TypeError, AttributeError):
            pass
    return matching_processes

def kill_process(file, filename, args):
    processes = get_processes(args)
    if type(args) is list:
        for proc in args:
            kill_process(file, filename, proc)
    if len(processes) == 0:
        output('kill process: Could not find process {}!'.format(args), filename, file)
    try:
        for proc in processes:
            proc.kill()
            output('kill process: Killed {} (pid: {}).'.format(proc.name(), proc.pid), filename, file)
    except (psutil.NoSuchProcess, psutil.ZombieProcess, TypeError, AttributeError):
        pass
    except psutil.AccessDenied:
        output('kill process: Could not kill process {} (pid: {})! Permission denied!'.format(proc.name(), proc.pid), filename, file)


def suspend_process(file, filename, args):
    processes = get_processes(args)
    if type(args) is list:
        for proc in args:
            suspend_process(file, filename, proc)
    if len(processes) == 0:
        output('suspend process: Could not find process {}!'.format(args), filename, file)
    try:
        for proc in processes:
            proc.suspend()
            output('suspend process: Suspended {} (pid: {}).'.format(proc.name(), proc.pid), filename, file)
    except (psutil.NoSuchProcess, psutil.ZombieProcess, TypeError, AttributeError):
        pass
    except psutil.AccessDenied:
        output('suspend process: Could not suspend process {} (pid: {})! Permission denied!'.format(proc.name(), proc.pid), filename, file)


def resume_process(file, filename, args):
    processes = get_processes(args)
    if type(args) is list:
        for proc in args:
            resume_process(file, filename, proc)
    if len(processes) == 0:
        output('resume process: Could not find process {}!'.format(args), filename, file)
    try:
        for proc in processes:
            proc.kill()
            output('resume process: Resumed {} (pid: {}).'.format(proc.name(), proc.pid), filename, file)
    except (psutil.NoSuchProcess, psutil.ZombieProcess, TypeError, AttributeError):
        pass
    except psutil.AccessDenied:
        output('resume process: Could not resume process {} (pid: {})! Permission denied!'.format(proc.name(), proc.pid), filename, file)