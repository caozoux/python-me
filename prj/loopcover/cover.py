import os

diskcache={}
disklist=[]
for line in open("log", 'r').readlines():
    sector=line[:-1].split(" ")
    print(sector)
    #print(int((int(sector[0])*512)/0x10000))
    offstr=str((int((int(sector[0])*512)/0x10000)))
    diskcache[offstr] = '1'

print(diskcache)
for key in diskcache:
    disklist.append(int(key))
    print(key)
disklist.sort()
print(disklist)
