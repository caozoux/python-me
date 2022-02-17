import os
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--format", action="store_true", dest="format",
                  help="--format -n number -c $commid format patch")
parser.add_option("-c", "--commit", type="string", dest="commit",
                  help="--commit kernel/initramfs/busbox")
parser.add_option("-n", "--number", type="string", dest="more",
                  help="--more kernel/initramfs/busbox")
parser.add_option("-u", "--busyboxinitramfs", type="string", dest="busyboxramfs",
                  help="--busyboxinitramfs kernel/initramfs/busbox")
parser.add_option("-m", "--patchopt", action="string", dest="patchopt",
                  help="--pachopt patch opte format/")
parser.add_option("-a", "--patchopt", action="string", dest="patchopt",
                  help="--pachopt patch opte format/")
(options, args) = parser.parse_args()

