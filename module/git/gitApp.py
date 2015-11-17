#!/usr/bin/env python

import os
import sys,time
import subprocess
from clrpr import clrprt

#patch_src="/extend/disk1G1/work/ti-am334x/ti-linux-kernel/"
#patch_dst="/extend/disk1G1/work/ti-am334x/kernel-3.14.x/"
#global patch_src
#global patch_dst

def runcmd(cmd, cmdshow=0):
    if cmdshow:
        print(cmd)
    return os.popen(cmd).read()

def context_cut_filt(contex,d_arg,f_arg, cmdshow=0):
    "run the command echo $contex | cut -d d_arg -f f_arg"
    cmd="echo \""+contex+"\" | cut -d "+d_arg+" -f "+f_arg
    if cmdshow:
        print(cmd)
    return os.popen(cmd).read()

def path_modefy_files(filename):
    "print the modefy files in one patch"
    if not os.path.exists(filename):
        clrprt.printc(filename+" no find");
        return
    #clrprt.printc(filename);
    cmd="cat "+filename+" | grep \"+++ \""+" | cut -b 7-"
    cmdout=os.popen(cmd).read()

    #print(cmdout)
    return cmdout

def cmp_file(filename,src,dst):
    "cmp the file,if the same, return 0"
    src_file=src+filename
    dst_file=dst+filename
    if os.path.exists(src_file) and os.path.exists(dst_file):
        cmd="diff -q "+src_file+" "+dst_file
        print("           "+cmd)
        cmdout=os.popen(cmd).read()
        if not cmdout =="":
            return 1
        else:
            return 0
    return 1

def get_linuxmail_patch(patchname,maildir,  curdir="", cmp_upstream="\[ Upstream commit "):
    "throught the patchname, then get the same patch \
    form kernle mailline. \
    argments: \
        patchname: the patch name \
        maildir: the mailline dir \
        curdir: the format patch out"

    #get the commit id in upstream
    if curdir=="":
        cmd="pwd"
        curdir=os.popen(cmd).read()
    
    retstr=""
    upstream_commit_num=0
    commitid=""
    cmd="cat "+patchname+" | grep \""+cmp_upstream+"\""
    cmdout=os.popen(cmd)
    for line in cmdout.readlines():

        if line == "":
            if upstream_commit_num==0:
                return "";
            else:
                if upstream_commit_num>1:
                    clrprt.printc("patch: "+patchname+" need your check")
                    return ""
                else:
                    return retstr
        else:
            commitid=line[18:-3]
            #clrprt.printc(commitid)
            cmd="cd "+maildir+"; "+"git show "+commitid
            cmdout1=os.popen(cmd).read()
            upstream_commit_num += 1
            cmd="cd "+maildir+"; "+"git format-patch -1 "+commitid+" -o "+curdir
            #print(cmd)
            retstr=os.popen(cmd).read()

    return retstr

def back_sdk_patch(patchname):
    " delete the line commit * upstream"
    cmd="cat "+patchname+" | grep -n \"\[zou: Original patch taken from\""
    cmdout=os.popen(cmd)
    for line in cmdout.readlines():
        if line == "":
            #clrprt.printc("it is invailb files")
            return
        else:
            number=context_cut_filt(line[:-1],":","1", 1)
            cmd="sed -i \""+number[:-1]+"d\" "+patchname
            print(cmd)
            if os.system(cmd):
                clrprt.printc(cmd+" is failed")
            if os.system(cmd):
                clrprt.printc(cmd+" is failed")
            if os.system(cmd):
                clrprt.printc(cmd+" is failed")


def format_sdk_patch(patchname, context, checkcontext):
    "add sdk patch context \
     context: sdk commit \
     checkcontext: if has the checkcontxt, just return"

    out=runcmd("cat "+patchname+" | grep -n \""+checkcontext+"\"",1)
    if not out=="":
        return
    out=runcmd("cat "+patchname+" | grep -n \" upstream$\"")
    if not out=="":
        return
    linecnt=""
    cmd="cat "+patchname+" | grep -n \"^---$\" | cut -d : -f 1"
    cmdout=os.popen(cmd).read()
    if cmdout == "":
        return
    else:
        linecnt=cmdout[:-1]
        cmd="sed -i '"+linecnt+" i"+context+"' "+patchname
        print(patchname)
        if os.system(cmd):
            clrprt.printc(cmd+" is failed")

def back_linuxmail_patch(patchname):
    " delete the line commit * upstream"
    cmd="cat "+patchname+" | grep -n \"upstream$\""
    cmdout=os.popen(cmd).read()
    if cmdout == "":
        #clrprt.printc("it is invailb files")
        return
    else:
        if cmdout[0]== "6" or cmdout[0]=="7" or cmdout[0]=="8" or cmdout[0]=="9":
            cmd="sed -i \"6,7d\" "+patchname
            if os.system(cmd):
                clrprt.printc(cmd+" is failed")
        else:
            clrprt.printc("it is invailb files")


def replace_mailine_patch(patchname, mailine_path="/home/wrsadmin/github/linux-stable"):
    "replace the patchname by using the mailine"
    inter_num=5
    cmdout=runcmd("cat "+patchname+" | grep -n \"upstream$\"")
    if not cmdout == "":
        clrprt.printc(patchname+" has upstream commit")
        return

    cmdout=runcmd("cat "+patchname+" | grep -n \"Subject:\" | cut -d ] -f 2")
    commit_context=cmdout[:-1]
    cmd="sed -n '5p' "+patchname
    cmdout2=os.popen(cmd).read()
    if len(cmdout2)<2:
        pass
    else:
        commit_context = commit_context + cmdout2[:-1]
        inter_num += 1

    shortlog=mailine_path+"/shortlog "
    cmdout2=runcmd("cat "+shortlog+" | grep -n "+"\""+commit_context+"\"")
    if len(cmdout2) > 10:
        clrprt.printc(patchname+" find upstream")
        number=runcmd("echo \""+cmdout2[:-1]+"\" | cut -d : -f 1")
        number=str((int(number[:-1])-3))
        out=runcmd("sed -n '"+number+"p' "+shortlog)
        commitid=out[7:-1]
        out=runcmd("git -C "+mailine_path+" format-patch -1 "+commitid+" -o "+runcmd("pwd"))
        runcmd("cp "+out[:-1]+" "+patchname, 1)

        f=open(patchname, 'r')
        number=0
        for line in f.readlines():
            number += 1
            #print(line[:-1]+"number: "+str(number)+"len: "+str(len(line)))
            if len(line) == 1:
                cmd="sed -i '"+str(number)+" acommit "+commitid+" upstream\\n'"+" "+patchname
                if os.system(cmd):
                    clrprt.printc(cmd+" is failed")
                break

            
        #runcmd("sed -i '"+str(inter_num)+" acommit "+commitid+" upstream\\n'"+" "+patchname

def is_mailine(patchname, mailgitlog="home/wrsadmin/github/linux-stable/shortlog", debug=0):
    "add  commit $commit upstream \
     to mailpatch"
    commitid=""

    inter_num=5
    cmd="cat "+patchname+" | grep -n \"upstream$\""
    cmdout=os.popen(cmd).read()
    if not cmdout == "":
        clrprt.printc(patchname+" has upstream commit")
        return 0
    cmd="cat "+patchname+" | grep -n \"Subject:\" | cut -d ] -f 2"
    cmdout=os.popen(cmd).read()
    commit_context=cmdout[:-1]
    #print(commit_context)
    cmd="sed -n '5p' "+patchname
    cmdout2=os.popen(cmd).read()

    if len(cmdout2)<2:
        pass
    else:
        commit_context = commit_context + cmdout2[:-1]
        inter_num += 1

    if (debug):
        print("%-20s %-20s"%(commit_context, patchname))

    commit_context =(commit_context.replace("\"","\\\""))
    commit_context =(commit_context.replace("$","\$"))
    commit_context =(commit_context.replace("[","\["))
    commit_context =(commit_context.replace("]","\]"))
    cmd="cat "+ mailgitlog+" | grep -n "+"\""+ commit_context+"\""
    cmdout2=os.popen(cmd).read()
    if len(cmdout2) > 10:
        return 1
    return 0

def format_linuxmail_patch(patchname):
    "add  commit $commit upstream \
     to mailpatch"
    commitid=""

    inter_num=5
    cmd="cat "+patchname+" | grep -n \"upstream$\""
    cmdout=os.popen(cmd).read()
    if not cmdout == "":
        clrprt.printc(patchname+" has upstream commit")
        return
    cmd="cat "+patchname+" | grep -n \"Subject:\" | cut -d ] -f 2"
    cmdout=os.popen(cmd).read()
    commit_context=cmdout[:-1]
    #print(commit_context)
    cmd="sed -n '5p' "+patchname
    cmdout2=os.popen(cmd).read()
    #print(cmdout2)
    if len(cmdout2)<2:
        pass
    else:
        commit_context = commit_context + cmdout2[:-1]
        inter_num += 1
    #print(commit_context)

    cmd="cat /home/wrsadmin/github/linux-stable/shortlog "+" | grep -n "+"\""+commit_context+"\""
    cmdout2=os.popen(cmd).read()
    if len(cmdout2) > 10:
        #print(cmdout2)
        clrprt.info(patchname+" find upstream")
        number=runcmd("echo \""+cmdout2[:-1]+"\" | cut -d : -f 1")
        number=str((int(number[:-1])-3))
        out=runcmd("sed -n '"+number+"p' "+"/home/wrsadmin/github/linux-stable/shortlog")
        commitid=out[7:-1]
        cmd="sed -i '"+str(inter_num)+" acommit "+commitid+" upstream\\n'"+" "+patchname
        if os.system(cmd):
            clrprt.err(cmd+" is failed")

def check_patch_format(patchname, cmdshow=0, mailine="/fstlink/kernel-3.14.x/scripts/checkpatch.pl "):
    " use the kernel/scripte/checkpath.pya \
      to check the patch"
    if os.system(mailine+patchname):
        clrprt.err(patchname+" patch error")
        return 1;
    else:
        if not cmdshow == 0:
            clrprt.info(patchname+ " pass");
        return 0;

def cmp_shortlog(sdklog, dstlog):
    "find the log patch in dstlog from sdklog"
    cmd="cat sdklog"
    cmdout=os.popen(cmd)
    number
    for line in cmdout.readlines():
        if [ line[:7] == "commit" ]:
            print("find commit :"+line[9:-1])


def remove_exit_patch(target_dir, patch_dir):
    "it patches has been exited in target_dir, remove them in patch_dir"
    if len(sys.argv) == 1:
        print("$target_dir $patch_dir")
        print("$target_dir: the root git")
        print("$patch_dir: patches directory")
        exit()

    rootdir=sys.argv[1]
    git_targ="/export/ti/kernel-3.14.x/shortlog"
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
                if need_find == "":
                    continue
                cmd = "cat " + git_targ + " | grep \"" + need_find + "\""
                print(cmd)
                find_grep = os.popen(cmd).read()
                print(need_find)
                if find_grep !="":
                    print(find_grep[:-1])
                    clrprt.printc("it is exist")
                    #删除他们
                    os.system("rm " + filename)
                    break
            else:
                if readline_cnt > 6:
                    break
            readline_cnt +=1

        #there is dts file?
        #+++ b/arch/arm/boot/dts/am437x-gp-evm.dts
        if os.path.exists(filename[:-1]) and 0:
            cmd1 ="cat " + filename[:-1] + " | grep \"+++ \"" + " | grep \".dts$\""
            cont = os.popen(cmd1).read()
            if cont != "":
                #print(cmd1)
                #os.system("rm " + filename)
                pass


        if os.path.exists(filename[:-1]) and 0:
            cmd1 ="cat " + filename[:-1] + " | grep \"+++ \"" + " | grep \".dtsi$\""
            cont = os.popen(cmd1).read()
            if cont != "":
                #print(cmd1)
                #os.system("rm " + filename)
                pass
