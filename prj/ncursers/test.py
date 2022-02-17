#!/usr/bin/env python
from  os  import  system
import _thread
import time
import  curses

biocounts=0
reqcounts=0

def loop_thread():
    global biocounts
    global reqcounts
    global screen
    while 1:
        time.sleep(1)
        biocounts += 1
        reqcounts += 1
        screen.addstr( 3 ,  2 ,  "bio:" + str(biocounts))
        screen.addstr( 4 ,  2 ,  "request:" + str(reqcounts))
        screen.refresh()


screen=curses.initscr()
curses.noecho()
screen.clear()
screen.border( 0 )
screen.addstr( 2 ,  2 ,  "block io stat" )
screen.addstr( 3 ,  2 ,  "bio:" + str(biocounts))
screen.addstr( 4 ,  2 ,  "request:" + str(reqcounts))
screen.refresh()
_thread.start_new_thread(loop_thread, ())
while 1:
    x=screen.getch()
    if  x  ==  ord ( '1' ):
        continue
    curses.endwin()
    break;
