import os
import sys
import re,time
#import commands

def excule_cmd_pr(cmd, is_show):
    cont = os.popen(cmd).read()
    if is_show:
        print(cont)
    return cont
    
def get_git_lot(path, save_name = "gitlog"):
    cmd = "cd " + path +";  git log | grep commit"
    if os.path.exists(path): 
        cont = os.popen(cmd).read()
        f = open(save_name, 'w')
        f.write(cont)
        f.close()
        #print(cont)
    else:
        return
    return


def find_path_diff_for_file(s_dir, d_dir, filename, show_mode):
    "show_mode 1: show debug information"
    #print(s_dir, "  ", d_dir)
    if os.path.exists(s_dir) and os.path.exists(d_dir):
        s_file= s_dir + "/" + filename;
        d_file= d_dir + "/" + filename;
        #print(s_file, "  ", d_file)
        if os.path.exists(s_file) and os.path.exists(d_file):
            cmd="diff -p" + " " + s_file + " " + d_file
            cont = os.popen(cmd).read()
            str_len=len(cont)


            if str_len > 20:
                #print('\033[1;31;40m')
                #print("~~~~~~~~~~~~~~log commit:"+s_file,)
                #print('\033[0m')
                #执行git log --pretty=oneline 去查看源文件修改记录
                cmd1= "cd "+ s_dir +"; "+"git log --pretty=oneline "+ filename + "| cut -b 42-"
                s_cont = excule_cmd_pr(cmd1, 0)

                ss_cont=(s_cont.replace("\n","^")).split("^")


                #执行git log --pretty=oneline 去查看目的文件修改记录
                #print('\033[1;31;40m')
                #print("~~~~~~~~~~~~~~log commit:"+d_file,)
                #print('\033[0m')
                cmd1= "cd "+ d_dir +"; "+"git log --pretty=oneline "+ filename + "| cut -b 42-"
                d_cont = excule_cmd_pr(cmd1, 0)

                dd_cont=(d_cont.replace("\n","^")).split("^")


                ss_rec_list = [ 0 for i in range(len(ss_cont))]
                dd_rec_list = [ 0 for i in range(len(dd_cont))]

                #比较两个文件记录的差异
                if show_mode == 1:
                    print('\033[1;31;40m')
                    print("~~~~~~~~~~~~~~exit patchs~~~~~~~~~~~~~~:")
                    print(s_file, "  compare:");
                    print(d_file)
                    print('\033[0m')

                s_ii = 0
                for s_i in ss_cont:
                    d_ii = 0
                    for d_i in dd_cont:
                        if len(s_i) == 0 or len(d_i) == 0 or dd_rec_list[d_ii] == 1:
                            pass
                        else:
                            if  s_i == d_i:
                                if show_mode == 1:
                                    print(s_ii, s_i, "<===>", len(d_i), d_ii)
                                dd_rec_list[d_ii] = 1
                                ss_rec_list[s_ii] = 1
                                break
                            else:
                                pass
                                #print(len(s_i), s_i, "<--->", len(d_i), d_i)
                        d_ii += 1
                    s_ii += 1

                #
                if 1:
                    print('\033[1;31;40m')
                    print("~~~~~~~~~~~~~~lost patch~~~~~~~~~~~~~~:")
                    print(s_file)
                    print('\033[0m')

                cmd1= "cd "+ s_dir +"; "+"git log --pretty=oneline "+ filename 
                s_cont = excule_cmd_pr(cmd1, 0)
                ss_cont=(s_cont.replace("\n","^")).split("^")

                for i in range(len(ss_rec_list)):
                    if ss_rec_list[i] == 0:
                        if len(ss_cont[i]):
                            print(ss_cont[i])
            else:
                if not os.path.exists(s_file):
                    print("file not exit :" + s_file)
                if not os.path.exists(d_file):
                    print("file not exit :" + d_file)
        else:
            if not os.path.exists(s_dir):
                print("file not exit :" + s_dir)
            elif not os.path.exists(d_dir):
                print("file not exit :" + d_dir)
            else:
                print("error")
            

            #print(cont)


if __name__ == "__main__":
    #get_git_lot("/export/disk1T1/bsp_work/TI_AM335X/kernel-3.10.x")
    if len(sys.argv) == 1:
        exit()

    if sys.argv[1].startswith('--'):
        option = sys.argv[1][2:]
        if option == 'dir':
            gitpath1 = sys.argv[2] + "/.git"
            gitpath2 = sys.argv[3] + "/.git"
            if os.path.exists(gitpath1) & os.path.exists(gitpath2):
                pass
            else:
                print(gitpath1, " or ", gitpath2, " isn't exist\n")
                exit()
            exit()
        elif option == 'dirsave':
            gitpath1 = sys.argv[2] + "/.git"
            gitpath2 = sys.argv[3] + "/.git"
            if os.path.exists(gitpath1) & os.path.exists(gitpath2):
                pass
            else:
                print(gitpath1, " or ", gitpath2, " isn't exist\n")
                exit()
        elif option == 'onefile':
            line_cnt = 0;
            if os.path.exists("config"):
                f = open('config', 'r')

                for line in f.readlines(): 
                    if line_cnt == 0:
                        gitpath1 = line[:-1]
                    if line_cnt == 1:
                        gitpath2 = line[:-1]
                    line_cnt += 1

            print("src: " + gitpath1)
            print("dst: " + gitpath2)
            print("start diff file: " + sys.argv[2]);
            find_path_diff_for_file(gitpath1, gitpath2, sys.argv[2], 0)
            exit()
    else:
        print("no enough argments")
        exit()

    

    f = open('files.list', 'r')
    if 1:
        for line in f.readlines(): 
            #line.replace("\n"," ")
            #print(len(line[:-1]), line)
            find_path_diff_for_file("/export/disk1T1/bsp_work/TI_AM335X/TI_SDK/ti-linux-kernel",
                    "/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x",
                    line[:-1], 0);
            #find_path_diff_for_file("/export/disk1T1/bsp_work/TI_AM335X/kernel-3.10.x",
            #        "/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x",
            #        line[:-1], 0);
    

    if 0:
        find_path_diff_for_file("/export/disk1T1/bsp_work/TI_AM335X/kernel-3.10.x",
                    "/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x",
                    "arch/arm/mach-omap2/am33xx-restart.c", 1);
