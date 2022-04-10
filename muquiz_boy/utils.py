import sys
import subprocess
from pathlib import Path
import os
from inspect import getsourcefile
import time

SRC_PATH = Path(os.path.abspath(getsourcefile(lambda:0))).parent

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def shell(*args):
    return subprocess.check_output(*args, shell=True)

def wait_until_connected(delay, trace=False):
    import urllib.request

    def try_connect(host='http://google.com'):
        try:
            urllib.request.urlopen(host) #Python 3.x
            return True
        except:
            return False

    while True:
        if try_connect():
            print('Connection successful!')
            return
        else:
            print(f'Connection failed... checking again in {delay}s')
            time.sleep(delay)


def dotted_access(
        dict_thing,
        path,
        separator='.',
        access=lambda d, k: d[k],
        process_k=lambda v: v,
        skip_first=False,
        also_get_parent=False
):
    res = dict_thing
    path_segs = path.split(separator)

    if skip_first:
        path_segs = path_segs[1:]

    parent = None
    for key in path_segs:
        key = process_k(key)

        parent = res
        res = access(res, key)

    return (res, parent) if also_get_parent else res
