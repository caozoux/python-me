import os
import pipes
import time
t = pipes.Template()
t.append('tr a-z A-Z', '--')
f = t.open('pipefile', 'r')

i = 0;
while i < 10:
    i += 1
    #f.write('hello world')
    cont = f.read()
    print(cont, "  ", i)
    if cont != '':
        print(f.read())

#f.close()
#print(open('pipefile').read())
