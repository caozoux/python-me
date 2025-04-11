#!/usr/bin/env python3

from pyme  import patchop;
from pyme  import patchcontext;
from pyme  import patchMerge;
from optparse import OptionParser;
import colorprint
import re;
import os;
import json


parser = OptionParser()
parser.add_option("-f", "--patch", dest="patchname",
                  help="assnig patch name", metavar="FILE")
parser.add_option("-m", "--merge",
                  action="store_true",  dest="opMerge",
                  help="-m -f file",
                  )
parser.add_option("-a", "--analysis",
                  action="store_true",  dest="showConflict",
                  help="-a -f $patch $lines, conflict start",
                  )
parser.add_option("-c", "--compare",
                  type="string",  dest="compare",
                  help="-c \"patch1 patch2\"",
                  )

(options, args) = parser.parse_args()

if options.opMerge:
    if os.path.exists(options.patchname):
        pass
    else:
        colorprint.err("err: "+options.patchname+" not exist")
        exit(1)
    patchname = options.patchname
    #commit = patchop.patchFilter.getCommit("/home/zoucao/github/linux-stable/patches/"+opatch.filelist[index][:-1])
    list = patchop.patchOperation.patchOpApply(patchname, flag=1)
    oPatchContext = patchcontext.patchcontext(patchname)
    oPatchContext.analysis()
    oPatchContext.dump()

    #print list
    for line in list:
        print("patch conflict "+line)
        var = re.sub("error: patch failed:.*:", "", line)
        var = var[:-1]
        oPatchModifyItem = oPatchContext.findPatchItemByLine(var)
        if oPatchModifyItem:
            oPatchModifyItem.dump_patch()
        else:
            colorprint.err("patch item not find: "+line)

        #oPatchModifyItem.showSrcAndItem()
        #oPatchModifyItem.mergeItem(oPatchModifyItem.mCmpStartline,0)
        #oMerge = patchMerge(oPatchModifyItem, oPatchModifyItem.mCmpStartline)

if options.showConflict:
    if not options.patchname:
        colorprint.err("err: options.patchname is null, please -f")
        exit(1)
    if not os.path.exists(options.patchname):
        colorprint.err("err: "+options.patchname+" not exist")
        exit(1)
    patchname = options.patchname
    oPatchContext = patchcontext.patchcontext(patchname)
    oPatchContext.analysis()
    oPatchContext.dump_patch()

    print(patchname)
    list = patchop.patchOperation.patchOpApply(patchname, flag=1)
    for line in list:
        print("patch conflict "+line)
        var = re.sub("error: patch failed:.*:", "", line)
        var = var[:-1]
        oPatchModifyItem = oPatchContext.findPatchItemByLine(var)
        if oPatchModifyItem:
            oPatchModifyItem.dump_patch()
            oPatchModifyItem.checkAddline("/export/disk1T/bsp_work/xilinx-zynq/linux-xlnx")
            #oPatchModifyItem.mergeItem(oPatchModifyItem.mCmpStartline,0)
        else:
            colorprint.err("patch item not find: "+line)
        patchMerge.patchMerge.mergeItem(oPatchModifyItem, "/export/disk1T/bsp_work/xilinx-zynq/linux-xlnx")

if options.compare:
    patch1, patch2 = re.sub(' +', ' ', options.compare).strip().split(" ")
    patch_src_obj= patchcontext.patchcontext(patch2)
    src_json = patch_src_obj.format_to_json()
    patch_dst_obj= patchcontext.patchcontext(patch1)
    dst_json = patch_dst_obj.format_to_json()
    for key,data in src_json.items():
        if not key in dst_json:
            print("err", key)
        src_diff_data = src_json[key]["patch_lines"]
        dst_diff_data = dst_json[key]["patch_lines"]
        src_diff_func = src_json[key]["patch_func"]
        dst_diff_func = dst_json[key]["patch_func"]

        src_diff_items = src_json[key]["patch_items"]
        dst_diff_items = dst_json[key]["patch_items"]

        find_diff = 0
        for item, value in src_diff_items.items():
            if not item in dst_diff_items.keys():
                #print("Err", item, value)
                continue

            dst_value = dst_diff_items[item]

            src_len = len(value)
            dst_len = len(dst_value)
            max_len = max(src_len, dst_len)
            if value != dst_value:
                for index in range(max_len):
                    src_line=""
                    dst_line=""
                    if index < len(value):
                        src_line = value[index]
                    if index < len(dst_value):
                        dst_line = dst_value[index]
                    if find_diff == 0:
                        colorprint.info(key)
                        find_diff = 1
                    if src_line[:-1] != dst_line[:-1]:
                        colorprint.warn("%-80s || %-80s"%(re.sub('\t', "",src_line[0:-1]), re.sub('\t', "",dst_line[0:-1])))
                    else:
                        print("%-80s || %-80s"%(re.sub('\t', "",src_line[0:-1]), re.sub('\t', "",dst_line[0:-1])))

                #print(value, dst_value)
        print("")

    for key,data in src_json.items():
        src_diff_items = src_json[key]["patch_items"]
        dst_diff_items = dst_json[key]["patch_items"]
        for item, value in src_diff_items.items():
            if not item in dst_diff_items.keys():
                colorprint.warn("Err:"+ item)
                for line in value:
                    print(line[:-1])
                continue

    #patch_dst_dict= patchcontext.patchcontext(patch2)
    #print(patch_src_dict)

