import sys
from glob import glob
from os.path import dirname, join, basename

curdir = dirname(__file__)
sys.path += [curdir]
files = glob(join(curdir, "hook_*.py"))

def after_apk_build(toolchain):
    for filename in files:
        modname = basename(filename)[:-3]
        module = __import__(modname)
        module.after_apk_build(toolchain)
