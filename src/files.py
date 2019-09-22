import os
import shutil

from jadmain import output


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


def append_file(file, filename, args, overwrite=False):
    def do_the_writey_thing(filz, writing, detailed_output=False):
        if type(filz) is list:
            files_written = 0
            for filzz in filz:
                files_written += do_the_writey_thing(filzz, writing)
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


def delete_file(file, filename, args):
    def do_deletion(thing, ignore_output=False):
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

    if not args or not (type(args) is list or type(args) is str):
        return output('delete file: Args is invalid! Must be a string or a list containing at least one string!', filename, file)
    do_deletion(args)