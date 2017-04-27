import os
def dbg(arg):
    if os.environ.get("pydbg") == "1":
        print(arg)
