import threading  
import time  
import logging  
import logging.handlers  

class thread_t1(threading.Thread):  
    def __init__(self,threadName):  
        threading.Thread.__init__(self,name = threadName)  
  
    def run(self):  
        i = 0
        while True:  
            i = i+1
            time.sleep(1)
            print(i) 

    
test = thread_t1("p1")
test.start()
