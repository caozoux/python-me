import os
import pipes
import time
t = pipes.Template()
t.append('tr a-z A-Z', '--')
f = t.open('pipefile', 'w')

i = 0;
while i < 10:
    i += 1
    time.sleep(1) 
    f.write('hello world')

#f.close()
#print(open('pipefile').read())
