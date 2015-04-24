import os

#Ñɫ´ò
def printc(dictArg, color="r"):
    "support color:  \
    r: red \
    g: green \
    y: yellow"
    if color == "r":
        print('\033[1;31;40m',end="")
    elif color == "g":
        print('\033[1;32;40m',end="")
    elif color == "y":
        print('\033[1;33;40m',end="")

    print(dictArg,end="")
    print('\033[0m')
    return 

def info(dictArg, color="r"):
    "green "
    print('\033[1;32;40m',end="")

    print(dictArg,end="")
    print('\033[0m')
    return 

def warn(dictArg, color="r"):
    "y: yellow"
    print('\033[1;33;40m',end="")

    print(dictArg,end="")
    print('\033[0m')
    return 

def err(dictArg, color="r"):
    "r: red"
    print('\033[1;31;40m',end="")

    print(dictArg,end="")
    print('\033[0m')
    return 
