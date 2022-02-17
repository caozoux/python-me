import subprocess

def excuteCommand(cmd, redirect=0, debug=0):
    if redirect:
        cmd = cmd + " 2>&1 "

    if debug:
        print(cmd)

    ex = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err  = ex.communicate()
    status = ex.wait()
    #print("cmd in:", com)
    #print("cmd out: ", out.decode())
    return out.decode()

#splite context to lines with \n, then print per line with number
def dumpline(context):
    lines=context.split("\n")
    for index in range(len(lines)):
        print(index, " ", lines[index])
