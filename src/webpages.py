import os

from jadmain import output

valid_ints = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def open_webpage(file, filename, args):
    def do_open_page(site):
        if not type(site) is str:
            if type(site) is list:
                for sitez in site:
                    do_open_page(sitez)
                return
            return output('open webpage: {} is not a string and thus cannot be a valid URL!'.format(site), filename, file)
        else:
            if not (site.startswith('http://') or site.startswith('https://') or site.startswith('localhost:') or site[0] in valid_ints):
                output('open webpage: Webpage {} does not start with http://, hhtps://, localhost:, or a number. Adding http:// to the beginning of the URL.'.format(site), filename, file)
                site = 'http://' + site
        os.system('start \"\" ' + site)

    if not args:
        return output('open webpage: Command cannot run without arguments!', filename, file)
    do_open_page(args)