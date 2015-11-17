#!/usr/bin/env python2.7
import os
import sys,time
import subprocess
#from clrpr import clrprt

g_patchname=""
def file_find_context_line(file,context):
    "it return the number, which find the context"
    context=context.replace("*","\\*")
    context=context.replace("$","\$")
    print("cat "+file+" | grep -n \""+context.replace("[","\[")+"\"")
    log=os.popen("cat "+file+" | grep -n \""+context.replace("[","\[")+"\"").read()
    if log == "":
        return "-1"
    return log.split(":")[0]

def file_get_line(file,line):
    "use sed to get file line"
    if isinstance(line,(int)):
        return os.popen("sed -n '"+str(line)+"p' "+file).read()[:-1]
    else:
        return os.popen("sed -n '"+line+"p' "+file).read()[:-1]

def get_patch_part_start_end(file, num, end=0):
    "get patch part between @@ and @@"
    flag=0
    log=os.popen("cat "+g_patchname+" | grep -n @@")
    for line in log.readlines():
        context=line.split(":")[1]
        if  flag:
            return line.split(":")[0]

        if num == context[4:context.find(",")]:
            #print(line)
            if end:
                return line.split(":")[0]
            flag = 1
    #it is the last @@
    return str(int(os.popen("cat "+g_patchname+" | wc -l").read()) - 1)

def git_find_conflit_palce(patch,file,start,end):
    "find the patch conflict start line number in src file" 
    start_cmp=os.popen("sed -n '"+start+"p' "+patch+" | cut -d @ -f 5").read()[1:-1]
    print(file)
    num=file_find_context_line(file,start_cmp)
    if num == -1:
        print("error: "+start_cmp+" no find");
        return 0;
    return int(num)
    
def git_conflit_cmpare_git(patch,file, patch_start,patch_end, file_start):
   #"patch: patch filename "
   #"file: src file"
   #"patch_start, patch_end: the rang of conflict of patch"
   #"file_start: the conflict start line in src fole"
    patch_cmp_start = int(patch_start)
    patch_cmp_end = int(patch_end)
    srcfile_cmp_start = int(file_start)
    git_start_line0=file_get_line(patch, str(int(patch_start)))[1:-1];
    git_start_line1=file_get_line(patch, str(int(patch_start)+1))[1:-1];
    git_start_line2=file_get_line(patch, str(int(patch_start)+2))[1:-1];
    git_start_line3=file_get_line(patch, str(int(patch_start)+3))[1:-1];
    print("git start0:"+git_start_line0.replace("\t","^I"))
    print("git start1:"+git_start_line1.replace("\t","^I"))
    print("git start2:"+git_start_line2.replace("\t","^I"))
    print("git start3:"+git_start_line3.replace("\t","^I"))
    srcfile_context=os.popen("sed -n '"+file_start+",400p' "+file)
    flag1=0
    flag2=0
    flag3=0
    for line in srcfile_context.readlines():
        srcfile_cmp_start += 1
        if flag1 == 0:
            if line.find(git_start_line1) >= 0:
                flag1 = 1
                print "start line1 right ",
                print(line.replace("\t","^I")[:-1])
        else:
            if flag2 == 0:
                if line.find(git_start_line2) >= 0:
                    flag2=1
                    print "start line2 right ",
                    print(line.replace("\t","^I")[:-1])
                else:
                    flag1 = 0
            else:
                if line.find(git_start_line3) >= 0:
                    print "start line3 right ",
                    print(line.replace("\t","^I")[:-1])
                    flag3 =1
                    break;
                else:
                    flag1 = 0
                    flag2 = 0
     
        
    # git the first 3 lines is passed
    if flag1 == 1 and flag2 == 1 and flag3 ==1:
        print("git start cmp is right")
        patch_cmp_start +=3
        patch_cmp_start +=1
        print str("patch").ljust(80), str("src").ljust(80)
        for number in range(patch_cmp_start, patch_cmp_end):
            line = file_get_line(patch, number)
            # start cmp the context with file 
            if line[0] != "+":
                patch_line=line.replace("\t","^I")
                src_line  =file_get_line(file, srcfile_cmp_start).replace("\t","^I")
                if src_line == patch_line[1:]:
                    print "issame",
                else:
                    print '\033[1;31;40m', "diff", '\033[0m',
                print number, line.replace("\t","^I").ljust(80),  srcfile_cmp_start, file_get_line(file, srcfile_cmp_start).replace("\t","^I")


                srcfile_cmp_start += 1

    
    else:
        print("git start cmp is wrong")
        return


# it is find the error lines when git apply failed
def git_applay(patchname):
    "git apply the $patchname, if error is occured, print the failed lines"

    p=subprocess.Popen("git apply "+patchname, stdin = subprocess.PIPE, \
            stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
    p.wait()
    #git apply fail
    if p.returncode:
        #errlog=p.stderr.read()
        pass
    else:
        return 1;

    #git failed, find the error line
    #testlog=errlog.strip()
    for line in p.stderr.readlines():
        if line.find("patch failed") > 1:
            filename=line.split(":")[2]
            start_num=line.split(":")[3][:-1] 
            end_num=get_patch_part_start_end(filename, start_num) #patch end line for conflict
            start_num=get_patch_part_start_end(filename, start_num,1) #patch line start for conflict
            conflic_line=git_find_conflit_palce(g_patchname,filename,start_num,end_num)
            if conflic_line == 0:
                exit();
            print(start_num+","+end_num+" patch:"+g_patchname)
            print(str(conflic_line)+" srcfile:"+filename)
            git_conflit_cmpare_git(g_patchname,filename,str(start_num),str(end_num),str(conflic_line))


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("argments is less")
        exit()

    g_patchname=sys.argv[1]
    git_applay(g_patchname)
