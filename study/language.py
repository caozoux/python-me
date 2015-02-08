#!/usr/bin/env python
import os

def if_lan():
    if x < 0:
        x = 0
        print('Negative changed to zero')
    elif x == 0:
        print('Zero')
    elif x == 1:
        print('Single')
    else:
        print('More')

def while_lan():
    words = ['cat', 'window', 'defenestrate']
    for w in words:
        print(w, len(w))


    for w in words[:]:
        if len(w) > 6:
            words.insert(0, w)

def rang_lan():
    print(rang(5,10))
#list 0, 0+3, 0+3+3 
    print(rang(0,10,3)) 
    print(rang(-10, -100, -30))
    a = ['Mary', 'had', 'a', 'little', 'lamb']
    for i in rang (len(a)):
        print(a,a[i])

def ask_ok_lan(prompt, retries=4, complaint='Yes or no, please!'):
    while True:
#input using method
        ok = input()
        print("you input is",ok)
        if ok in ('Y', 'Ye', 'Yes'):
            return True
        if ok in ('n', 'no', 'nop', 'nope'):
            return False
        retries = retries - 1
        if retries < 0:
            raise IOError('refusenik user')
        print(complaint)

def defaultList_lan(a, L=None):
    if L is None:
        L = []
    L.append(a)
    return L

def cheeseshop(kind, *arguments, **keywords):
    print("-- Do you have any", kind, "?")    
    print("-- I'm sorry, we're all out of", kind)
    for arg in arguments:
        print(arg)
    
    print("'-' * 40")
    keys = sorted(keywords.keys())
    for kw in keys:
        print(kw, ":", keywords[kw])


#cheeseshop("Limburger", "It's very runny, sir.",
#                "It's really very, VERY runny, sir.",
#                shopkeeper='Michael Palin',
#               client="John Cleese",
#              sketch="Cheese Shop Sketch")

#-- Do you have any Limburger ?
#-- I'm sorry, we're all out of Limburger
#It's very runny, sir.
#It's really very, VERY runny, sir.
#'-' * 40
#client : John Cleese
#shopkeeper : Michael Palin
#sketch : Cheese Shop Sketch

# a ? b : c
def make_incrementor(n):
        return lambda x: x + n


#printf the function help information
def my_function():
    """Do nothing, but document it.
    No, really, it doesn't do anything."""

    print my_function.__doc__

def list_lan():
#list.append(x)
#Add an item to the end of the list; equivalent to a[len(a):]
#= [x].
#list.extend(L)
#Extend the list by appending all the items in the given list; equivalent to a[len(a):]
#= L.
#list.insert(i, x)
#Insert an item at a given position. The first argument is the index of the element before which to in-
#sert, so a.insert(0, x) inserts at the front of the list, and a.insert(len(a), x) is equivalent to
#a.append(x).
#list.remove(x)
#Remove the first item from the list whose value is x. It is an error if there is no such item.
#list.pop( [ i ] )
#Remove the item at the given position in the list, and return it. If no index is specified, a.pop() removes
#and returns the last item in the list. (The square brackets around the i in the method signature denote that
#the parameter is optional, not that you should type square brackets at that position. You will see this notation
#frequently in the Python Library Reference.)
#list.index(x)
#Return the index in the list of the first item whose value is x. It is an error if there is no such item.
#list.count(x)
#Return the number of times x appears in the list.
#list.sort(cmp=None, key=None, reverse=False)
#Sort the items of the list in place (the arguments can be used for sort customization, see sorted() for their
#explanation).
#list.reverse()
#Reverse the elements of the list, in place.        
    print list_lan.__doc__

def queuq_lan():
    from collections import deque
    queue = deque(["elic1,elic2, elic3"])
    queue.append("Terry")
    queue.append("Graham")
    queue.popleft()


def f(x): return x % 3 == 0 or x % 5 == 0
#filter(f, range(2, 25))
#[3, 5, 6, 9, 10, 12, 15, 18, 20, 21, 24]
    

#map function
#def cube(x): return x*x*x
#map(cube, range(1, 11))
#seq = range(8)
#def add(x, y): return x+y
#map(add, seq, seq)
#[2, 4, 6, 8, 10, 12, 14]]
    
#def add(x,y): return x+y
#reduce(add, range(1, 11))

#=========================del function===================================
#a = [-1, 1, 66.25, 333, 333, 1234.5]
#del a[0]
#del a[2:4]
#del a
#


#=========================set function===================================
#>>> a = set('abracadabra')
#>>> b = set('alacazam')
#>>> a
## unique letters in a
#set(['a', 'r', 'b', 'c', 'd'])
#>>> a - b
## letters in a but not in b
#set(['r', 'd', 'b'])
#>>> a | b
## letters in either a or b
#set(['a', 'c', 'r', 'd', 'b', 'm', 'z', 'l'])
#>>> a & b
## letters in both a and b
#set(['a', 'c'])
#>>> a ^ b
## letters in a or b but not both
#set(['r', 'd', 'b', 'm', 'z', 'l'])
#Similarly to list comprehensions, set comprehensions are also supported:
#>>> a = {x for x in 'abracadabra' if x not in 'abc'}
#>>> a


#=========================diction===================================
#>>> tel = {'jack': 4098, 'sape': 4139}
#>>> tel['guido'] = 4127
#>>> tel
#{'sape': 4139, 'guido': 4127, 'jack': 4098}
#>>> tel['jack']
#4098
#>>> del tel['sape']
#>>> tel['irv'] = 4127
#>>> tel
#{'guido': 4127, 'irv': 4127, 'jack': 4098}
#>>> tel.keys()
#['guido', 'irv', 'jack']
#
#dict([('sape', 4139), ('guido', 4127), ('jack', 4098)])
#{'sape': 4139, 'jack': 4098, 'guido': 4127}


#=========================loop===================================
>>> for i, v in enumerate(['tic', 'tac', 'toe']):
#...
#print i, v
#...
#0 tic
#1 tac
#2 toe]
#>>> questions = ['name', 'quest', 'favorite color']
#>>> answers = ['lancelot', 'the holy grail', 'blue']
#>>> for q, a in zip(questions, answers):
#...
#print 'What is your {0}? It is {1}.'.format(q, a)
#...
#What is your name? It is lancelot.
#What is your quest? It is the holy grail.
#What is your favorite color? It is blue.diction
#>>> for i in reversed(xrange(1,10,2)):
#...
#print i
#9
#7
#5
#3
#1
#To loop over a sequence in sorted order, use the sorted() function which returns a new sorted list while leaving the
#source unaltered.
#>>> basket = ['apple', 'orange', 'apple', 'pear', 'orange', 'banana']
#>>> for f in sorted(set(basket)):
#...
#print f
#...
#apple
#banana
#orange
#pear
#>>> knights = {'gallahad': 'the pure', 'robin': 'the brave'}
#>>> for k, v in knights.iteritems():
    #...
#print k, v
#


