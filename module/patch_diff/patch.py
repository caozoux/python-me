import os
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

def find_path_diff_for_file(s_dir, d_dir, filename):
    if os.path.exists(s_dir) and os.path.exists(d_dir):
        s_file= s_dir + "/" + filename;
        d_file= d_dir + "/" + filename;
        if os.path.exists(s_file) and os.path.exists(d_file):
            cmd="diff" + " " + s_file + " " + d_file
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
                                print(len(s_i), s_i, "<===>", len(d_i), d_i)
                                dd_rec_list[d_ii] = 1
                                ss_rec_list[d_ii] = 1
                                break
                            else:
                                pass
                                #print(len(s_i), s_i, "<--->", len(d_i), d_i)
                        d_ii += 1
                    s_ii += 1

                print('\033[1;31;40m')
                print("~~~~~~~~~~~~~~lost patch~~~~~~~~~~~~~~:")
                print('\033[0m')

                for i in range(len(ss_rec_list)):
                    if ss_rec_list[i] == 0:
                        if len(ss_cont[i]):
                            print(ss_cont[i])
                

            #print(cont)


if __name__ == "__main__":
    #get_git_lot("/export/disk1T1/bsp_work/TI_AM335X/kernel-3.10.x")
    find_path_diff_for_file("/export/disk1T1/bsp_work/TI_AM335X/kernel-3.10.x",
                "/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x",
                "arch/arm/common/edma.c");
