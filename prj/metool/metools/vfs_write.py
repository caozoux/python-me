import os

#lines=open("/sys/kernel/debug/tracing/trace",'r').readlines()
lines=open("./log",'r').readlines()
exiting=0
dictprocess_write={}
dictprocess={}
for line in lines:
  items=line.split(";")
  #print(line)
  #print(items[1], items[2], items[3], items[4])
  comm = items[1]
  block = items[2]
  write_size = items[3]
  filename = items[4]
  if not comm in dictprocess.keys():
    task={}
    filewrite={}
    blockwrite={}
    dictprocess_write[comm] = int(write_size)
    blockwrite[block]= int(write_size)
    task["block"] = blockwrite
    task["write"] = int(write_size)
    task["write_cnt"] = 1
    #task[filename] = int(write_size)
    filewrite[filename]= int(write_size)
    dictprocess[comm] = task
    task["files"] =filewrite 
  else:
    dictprocess_write[comm] += int(write_size)
    task = dictprocess[comm]
    task["write_cnt"] += 1
    filewrite = task["files"]
    blockwrite = task["block"]
    if block in blockwrite.keys():
      blockwrite[block] += int(write_size)
    else:
      blockwrite[block] = int(write_size)
    if filename in filewrite.keys():
      filewrite[filename] += int(write_size)
    else:
      filewrite[filename] = int(write_size)
    task["write"] += int(write_size)


#for key in  dictprocess.keys():
#  print(key, dictprocess[key])
#print(dictprocess_write)

for key, value in sorted(dictprocess_write.items(), key = lambda x: x[1]):
  task=dictprocess[key]
  filewrite=dictprocess[key]["files"]
  blockwrite = task["block"]
  print("task: %-15s write size:%-15d writecnt:%-15d"%(key, value, task["write_cnt"])) 
  for key in blockwrite.keys():
    print("%-10s:%-10d"%(key, blockwrite[key])
  for filekey in filewrite.keys():
    print("    filename:%-30s:%d"%(filekey, filewrite[filekey]))
  
