import os
import os.path
rootdir = "/export/disk1T1/bsp_work/TI_AM335X/kernel-cache/bsp/ti-am335x"
kernel_dir="/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x"

#for parent,dirnames,filenames in os.walk(rootdir):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
#    for dirname in  dirnames:                       #输出文件夹信息
#        print("parent is:" + parent)
#        print("dirname is" + dirname)
#    for filename in filenames:                        #输出文件信息
#        print("parent is:" + parent)
#        print("filename is:" + filename)
#        print("the full name of the file is:" + os.path.join(parent,filename)) #输出文件路径信息

cmd="cat " + rootdir +"/*"
cont = os.popen(cmd)
for line in cont.readlines():
    #print(line)
    #if line [:7]
    if line[:7] == "(cherry":
        commit_id = line[27:-2]
        cmd1= "cd "+ kernel_dir +"; "+"git show -s --format=%s " + commit_id
        gitshow_cont = os.popen(cmd1).read()
        #print(gitshow_cont)
        #print(gitshow_cont[:20])
        if gitshow_cont[:5] == "":
            print("lost path:"+ commit_id)
    
    #print(line[:8])

    #(cherry picked from commit
