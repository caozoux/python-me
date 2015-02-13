import os

def dump_files(file_name):
    with open(file_name, 'r') as f:
        line = 0
        for line_cnt in f.readlines():
            print(line, line_cnt)
            line += 1

def dump_files_with_filter(file_name, start_line=0, end_line=10000):
    "get file line between start_line and end_line"
    with open(file_name, 'r') as f:
        line = 0
        for line_cnt in f.readlines():
            if (line>=start_line) and (line<=end_line):
                #print(line_cnt, line)
                print(line_cnt)
            line += 1
    return

if __name__ == '__main__':
    #dump_files("/home/wrsadmin/cach/gitlog")
    dump_files_with_filter("/home/wrsadmin/cach/gitlog", 474, 591)
