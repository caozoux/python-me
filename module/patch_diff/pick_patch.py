#the script filtes the patch, which is in the upsteam


import os
import sys
import re,time
#import commands

dbg_cnt = 0

def check_gitpatch(git_root, patch):
    f = open(patch, 'r')
    for line in f.readlines(): 
        if line[:4] =="+++ ":



if __name__ == "__main__":
    #gitlog的时间
    cmd_time=""
    autor_name=""
    #get_git_lot("/export/disk1T1/bsp_work/TI_AM335X/kernel-3.10.x")
    if len(sys.argv) == 1:
        exit()

    if sys.argv[1].startswith('--'):
        option = sys.argv[1][2:]
        if option == 'dir':
            patches_dir = sys.argv[2]
            if os.path.exists(patches_dir):
                cmd="ls " + patches_dir + " | sort"
                for line in os.popen(cmd).readlines():
                    patch_f = patches_dir + "/" + line[:-1]
                    cmd1="cat " + patch_f + " | grep \"Upstream[- ]commit\""
                    cont = os.popen(cmd1).read()
                    #print(cont)
                    if cont != "":
                        print("find upstream patch: ", patch_f)
                        print("commit: " + cont[-44:-2])
                    else:
                        print("find patch: ", patch_f)
                        #检测patch的代码是否在kernel里
                    dbg_cnt += 1
                    if dbg_cnt > 20:
                        exit()
            else:
                print("dir isn't exist")
                exit()
