import os
from optparse import OptionParser

class kernel(object):

    """Docstring for kernel. """

    def __init__(self):
        """TODO: to be defined. """

    def test(self):
        """TODO: Docstring for test.

        :arg1: TODO
        :returns: TODO

        """
        print("kernel test")

def kerneltest(arg1):
    """TODO: Docstring for kerneltest.

    :arg1: TODO
    :returns: TODO

    """
    print("ker zz")


#                  action="store", type="int", default="1", dest="threadsCount",
parser = OptionParser()
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list show all commands info")

parser.add_option("-m", "--more", type="string", dest="more",
                  help="--more kernel/initramfs/busbox")
parser.add_option("-B", "--busyboxinitramfs", type="string", dest="busyboxramfs",
                  help="--busyboxinitramfs kernel/initramfs/busbox")
#parser.add_option("-p", "--patchopt", action="string", dest="patchopt",
#                  help="--pachopt patch opte format/")
(options, args) = parser.parse_args()

if options.busyboxramfs:
    os.system("cd " + options.busyboxramfs + " && mkdir -p etc/init.d && cd -")
    os.system("cd " + options.busyboxramfs + " && echo  \"!#/bin/sh\nmount -t devtmpfs devtmpfs /dev \nmkdir -p /dev/pts\nmount -vt devpts -o gid=4,mode=620 none /dev/ptx\n \" > etc/init.d/rcS && chmod 755 etc/init.d/rcS && cd -")
    os.system("cd " + options.busyboxramfs + " && find . | cpio -o --format=newc > root_fs.cpio")

#elif options.patchopt:
#    if options.patchopt == "format":
        #check it is kernel upstream
#        lines=os.popen("git remote -v").readlines()
