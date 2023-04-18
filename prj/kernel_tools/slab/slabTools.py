#!/bin/python3


import os
import re


from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--interface", type="string", dest="interface",
                  help="--interface ")

parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
(options, args) = parser.parse_args()



if options.interface:
    if not os.path.exists(options.interface):
        print("not find", options.interface);
        exit(1)
else:
    print("specify slab interface proc file ")
    exit(1)


lines=open(options.interface, "r").readlines()
#Title=["name", "<active_objs>", "<num_objs>", "<objsize>", "<objperslab>", "<pagesperslab>", ":", "tunables", "<limit>", "<batchcount>", "<sharedfactor>", ":", "slabdata", "<active_slabs>", "<num_slabs>", "<sharedavail>"]

slabdict={}
res= re.sub(" +"," ", lines[1][2:-1].strip())
Title = res.split(" ")
for line in lines[2:]:
    res= re.sub(" +"," ", line[:-1].strip())
    array = res.split(" ")
    name = array[0]
    pagesperslab = int(array[5])
    num_slabs = int(array[14])
    total_pages = pagesperslab * num_slabs
    slabdict[name] = total_pages
    #print(Title[5], pagesperslab,  Title[14], num_slabs)

res=sorted(slabdict.items(), key=lambda item:item[1])
for item in res:
    print("", item);

