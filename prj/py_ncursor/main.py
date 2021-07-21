import sys
import os
import time

SchedStatList_cpu0_data_list=[]
SchedStatList_cpu0_data=[]
SchedStatList_cpu0=[]
SchedStatList=[]

#seq_printf(seq,
#"cpu%d %u 0 %u %u %u %u %llu %llu %lu",
#cpu, rq->yld_count,
#rq->sched_count, rq->sched_goidle,
#rq->ttwu_count, rq->ttwu_local,
#rq->rq_cpu_time,
#rq->rq_sched_info.run_delay, rq->rq_sched_info.pcount

def SchedShowDiff(data):
    print("   ", end="")
    for item in data:
        if item == 0:
            print("- ", end="")
        else:
            print(item," ", end="")
    print()

def SchedFuncDiff(data1, data2):
    data_list=[]
    for num in range(0,10):
        #print(int(data2[num]) - int(data1[num]))
        data_list.append(int(data2[num]) - int(data1[num]))
    return data_list


print("cpu yld_count sched_count sched_goidle ttwu_count ttwu_local rq_cpu_time run_delay pcount\n");
#cpu, rq->yld_count,
#rq->sched_count, rq->sched_goidle,
#rq->ttwu_count, rq->ttwu_local,
#rq->rq_cpu_time,
#rq->rq_sched_info.run_delay, rq->rq_sched_info.pcount
for num in range(0,10):
    fd=os.open("/proc/schedstat", os.O_RDONLY)
    buffer=os.read(fd, 16024)

    ProcBufList=buffer.decode().splitlines()[1:]
    #for line in ProcBufList:
    #    print(line)
    SchedStatList.append(ProcBufList)
    os.close(fd)
    time.sleep(1)
    cpu0=ProcBufList[1]
    SchedStatList_cpu0_data_list.append(cpu0[3:].split(" "))
    print(cpu0)
    SchedStatList_cpu0.append(cpu0)
    if num != 0:
        offdata=SchedFuncDiff(SchedStatList_cpu0_data_list[num-1], SchedStatList_cpu0_data_list[num])
        SchedShowDiff(offdata)

