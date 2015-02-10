>>> import os
>>> os.getcwd()
# Return the current working directory
'C:\\Python26'
>>> os.chdir('/server/accesslogs')
# Change current working directory
>>> os.system('mkdir today')
# Run the command mkdir in the system shell
0



>>> import shutil
>>> shutil.copyfile('data.db', 'archive.db')
>>> shutil.move('/build/executables', 'installdir')


>>> import glob
>>> glob.glob('*.py')
['primes.py', 'random.py', 'quote.py']

>>> import sys
>>> print sys.argv
['demo.py', 'one', 'two', 'three']


>>> import urllib2
>>> for line in urllib2.urlopen('http://tycho.usno.navy.mil/cgi-bin/timer.pl'):
...
if 'EST' in line or 'EDT' in line: # look for Eastern Time
...
print line
<BR>Nov. 25, 09:43:32 PM EST
>>>
>>>
>>>
...
...
...
...
...
>>>
import smtplib
server = smtplib.SMTP('localhost')
server.sendmail('soothsayer@example.org', 'jcaesar@example.org',
"""To: jcaesar@example.org
From: soothsayer@example.org
Beware the Ides of March.
""")
server.quit()


>>> import zlib
>>> s = 'witch which has which witches wrist watch'
>>> len(s)
41
>>> t = zlib.compress(s)
>>> len(t)
37
>>> zlib.decompress(t)
'witch which has which witches wrist watch'
>>> zlib.crc32(s)
226805979

import logging
logging.debug('Debugging information')
logging.info('Informational message')
logging.warning('Warning:config file %s not found', 'server.conf')
logging.error('Error occurred')
logging.critical('Critical error -- shutting down')



