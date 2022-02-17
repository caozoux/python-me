import subprocess

def excuteCommand(cmd, redirect=0):
    if redirect:
        cmd = cmd + " 2>&1 "

    ex = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err  = ex.communicate()
    status = ex.wait()
    #print("cmd in:", com)
    #print("cmd out: ", out.decode())
    return out.decode()
