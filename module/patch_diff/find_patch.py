import os
import os.path
import sys
rootdir ="/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x/cach/patch100/"
kernel_dir="/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x/patches_ti"
git_targ="/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x/shortlog"

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
            cmd = "cat " + git_targ + " | grep \"" + need_find + "\""
            find_grep = os.popen(cmd).read()
            print(need_find)
            if find_grep !="":
                print(find_grep[:-1])
                print("it is exist")
                #删除他们
                os.system("rm " + filename)
            #cmd = "cat " + filename[:-1]+ " | grep \"+++ \""
            #modef_file_name = os.popen(cmd).read()
            #print(modef_file_name[6:-1])
            #print(cmd)
            #检测文件是否三有效的

            #print(cmd)
        readline_cnt +=1
    
    #print(line[:8])

    #(cherry picked from commit
