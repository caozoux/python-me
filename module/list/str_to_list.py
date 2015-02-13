import os

def str_to_list(cont):
    #hex_number=(cont.replace("\n","^")).split("^")
    hex_number=cont.split("\n")
    for i in hex_number:
            print(i)


if __name__ == "__main__":
    str_to_list("abc\ndef\nghij\n")
