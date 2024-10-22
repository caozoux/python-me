#!/bin/python3
import time
from datetime import datetime
def get_process_times(pid):
    try:
        # 打开指定进程的 stat 文件
        with open(f'/proc/{pid}/stat', 'r') as file:
            # 读取文件内容
            stat_info = file.read().strip().split()
            # 根据 proc stat 格式获取 cutime 和 stime
            # cutime 在第 14 位，stime 在第 15 位（从 0 开始计数）
            cutime = int(stat_info[13])  # 用户时间
            stime = int(stat_info[14])    # 系统时间
            return int(cutime), int(stime)
    except FileNotFoundError:
        print(f"进程 {pid} 不存在。")
        return None, None
    except Exception as e:
        print(f"发生错误: {e}")
        return None, None

old_cutime, old_stime = get_process_times(1)
if __name__ == "__main__":
    while  1 :
        start_time = datetime.now()
        time.sleep(1)
        # 替换为你要监控的进程 ID
        cutime, stime = get_process_times(1)
        now = datetime.now()
        delta = (now - start_time).total_seconds()

        if cutime is not None and stime is not None:
            print("用户时间 %d 系统时间 %d %s (%d %d %f)"%(cutime - old_cutime, stime - old_stime, now.strftime("%Y-%m-%d %H:%M:%S"), (cutime - old_cutime)/delta, (stime - old_stime)/delta, delta))
        else:                                                                                                                   
            print("无法获取进程信息")                                                                                         
        old_cutime = cutime                                                                                                     
        old_stime = stime 
