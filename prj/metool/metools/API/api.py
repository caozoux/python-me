import subprocess
import os

def excuteCommand(cmd, redirect=0, debug=0, stdshow=0):
    if redirect:
        cmd = cmd + " 2>&1 "

    if debug:
        print(cmd)

    #ex = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    if stdshow:
        ex = subprocess.Popen(cmd, stdout=None, shell=True)
        status = ex.wait()
        return status
    else:
        ex = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        status = ex.wait()
        out, err  = ex.communicate()
        return out.decode()

#splite context to lines with \n, then print per line with number
def dumpline(context):
    lines=context.split("\n")
    for index in range(len(lines)):
        print(index, " ", lines[index])

def FileRead(filename, line=-1):
    res=""
    filename=os.path.expanduser(filename)
    if not os.path.exists(filename):
        return res

    fd=open(filename, "r")
    if line != -1:
        res=fd.readline(line)
    else:
        res=fd.read()

    fd.close()
    return res

