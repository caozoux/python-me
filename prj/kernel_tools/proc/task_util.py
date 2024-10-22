#!/bin/python3
import time
from datetime import datetime

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-p", "--pid", dest="pid", type="int",
                  help="--pid specify pid")
(options, args) = parser.parse_args()

def get_process_times(pid):
    try:
        # 打开指定进程的 stat 文件
        with open(f'/proc/{pid}/stat', 'r') as file:
            # 读取文件内容
            stat_info = file.read().strip().split()
            # 根据 proc stat 格式获取 ctime 和 stime
            # ctime 在第 14 位，stime 在第 15 位（从 0 开始计数）
            ctime = int(stat_info[13])  # 用户时间
            stime = int(stat_info[14])    # 系统时间
            return int(ctime), int(stime)
    except FileNotFoundError:
        print(f"进程 {pid} 不存在。")
        return None, None
    except Exception as e:
        print(f"发生错误: {e}")
        return None, None

if __name__ == "__main__":
    if not options.pid:
        print("Error: not specify pid")
        exit(1)

    old_ctime, old_stime = get_process_times(options.pid)
    while  1 :
        start_time = datetime.now()
        time.sleep(1)
        # 替换为你要监控的进程 ID
        ctime, stime = get_process_times(options.pid)
        now = datetime.now()
        delta = (now - start_time).total_seconds()

        if ctime is not None and stime is not None:
            print("%s user: %d sys: %d "%(now.strftime("%H:%M:%S"), ctime - old_ctime, stime - old_stime))
        else:
            print("无法获取进程信息")
        old_ctime = ctime
        old_stime = stime
