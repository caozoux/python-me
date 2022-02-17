import os
import getopt

try:
    # Short option syntax: "hv:"
    # Long option syntax: "help" or "verbose="
    opts, args = getopt.getopt(sys.argv[1:], "short_options", [long_options])

except getopt.GetoptError, err:
    # Print debug info
    print str(err)
    error_action

for option, argument in opts:
    if option in ("-h", "--help"):
        
    elif option in ("-v", "--verbose"):
        verbose = argument

    elif option in ("-v", "--verbose"):
        verbose = argument
