def info(dictArg):
    "green "
    print '\033[1;32;32m',
    print dictArg,
    print '\033[0m'
    return

def warn(dictArg, color="r"):
    "y: yellow"
    print '\033[1;33;33m',
    print dictArg,
    print '\033[0m'
    return

def err(dictArg, color="r"):
    "r: red"
    print '\033[1;31;31m',
    print dictArg,
    print '\033[0m'
    return

def blue(dictArg, color="r"):
    "r: red"
    print '\033[1;34;34m',
    print dictArg,
    print '\033[0m'
    return
