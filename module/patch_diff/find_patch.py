import os
import os.path
import sys
rootdir ="/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x/cach/patch100/"
kernel_dir="/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x/patches_ti"
git_targ="/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x/shortlog"
#git_targ="/extend/disk1G1/work/github/linux-stable/shortlog"

#for parent,dirnames,filenames in os.walk(rootdir):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
#    for dirname in  dirnames:                       #输出文件夹信息
#        print("parent is:" + parent)
#        print("dirname is" + dirname)
#    for filename in filenames:                        #输出文件信息
#        print("parent is:" + parent)
#        print("filename is:" + filename)
#        print("the full name of the file is:" + os.path.join(parent,filename)) #输出文件路径信息

if len(sys.argv) == 1:
    exit()
rootdir=sys.argv[1]
cmd="ls " + rootdir +"/*.patch | sort"
file_list = os.popen(cmd)
for filename in file_list.readlines():
    #print(line)
    #if line [:7]
    cmd1 ="cat " + filename
    cont = os.popen(cmd1)
    print(filename[:-1])

    readline_cnt = 0
    for line in cont.readlines():
        if readline_cnt == 3:
            need_find = line[27:-1]
        elif readline_cnt == 4:
            if len(line) <= 2:
                pass
            else:
                #extand_cont=line[:-1]
                #need_find = need_find + extand_cont
                #print(extand_cont)
                pass
            need_find =(need_find.replace("\"","\\\""))
            need_find =(need_find.replace("$","\$"))
            need_find =(need_find.replace("[","\["))
            need_find =(need_find.replace("]","\]"))
            cmd = "cat " + git_targ + " | grep \"" + need_find + "\""
            print(cmd)
            find_grep = os.popen(cmd).read()
            print(cmd)
            print(need_find)
            if find_grep !="":
                print(find_grep[:-1])
                print("it is exist")
                #删除他们
                os.system("rm " + filename)
                break
        else:
            if readline_cnt > 6:
                break
        readline_cnt +=1

    #there is dts file?
    #+++ b/arch/arm/boot/dts/am437x-gp-evm.dts
    if os.path.exists(filename[:-1]):
        cmd1 ="cat " + filename[:-1] + " | grep \"+++ \"" + " | grep \".dts$\""
        cont = os.popen(cmd1).read()
        if cont != "":
            print(cmd1)
            os.system("rm " + filename)


    if os.path.exists(filename[:-1]):
        cmd1 ="cat " + filename[:-1] + " | grep \"+++ \"" + " | grep \".dtsi$\""
        cont = os.popen(cmd1).read()
        if cont != "":
            print(cmd1)
            os.system("rm " + filename)
    
    #print(line[:8])

    #(cherry picked from commit
