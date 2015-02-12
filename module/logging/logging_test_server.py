import logging, logging.handlers
import time

# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create buffer handle
#chm = logging.MemoryHandler()
#chm.setLevel(logging.DEBUG)


# create buffer handle
#chm = logging.handlers.SocketHandler("localhost", 20011)
chm=logging.handlers.SocketHandler("localhost", 2001)
#chm.setLevel(logging.DEBUG)
#chma.makeSocket()

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(chm)

# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warn('warn message')
logger.error('error message')
logger.critical('critical message')




#1. "StreamHandler" instances send messages to streams (file-like
#   objects).

#2. "FileHandler" instances send messages to disk files.
#
#3. "BaseRotatingHandler" is the base class for handlers that rotate
#   log files at a certain point. It is not meant to be  instantiated
#   directly. Instead, use "RotatingFileHandler" or
#   "TimedRotatingFileHandler".
#
#4. "RotatingFileHandler" instances send messages to disk files,
#   with support for maximum log file sizes and log file rotation.
#
#5. "TimedRotatingFileHandler" instances send messages to disk
#   files, rotating the log file at certain timed intervals.
#
#6. "SocketHandler" instances send messages to TCP/IP sockets.
#
#7. "DatagramHandler" instances send messages to UDP sockets.
#
#8. "SMTPHandler" instances send messages to a designated email
#   address.
#
#9. "SysLogHandler" instances send messages to a Unix syslog daemon,
#   possibly on a remote machine.
#
#10. "NTEventLogHandler" instances send messages to a Windows
#    NT/2000/XP event log.
#
#11. "MemoryHandler" instances send messages to a buffer in memory,
#    which is flushed whenever specific criteria are met.
#
#12. "HTTPHandler" instances send messages to an HTTP server using
#    either "GET" or "POST" semantics.
#
#13. "WatchedFileHandler" instances watch the file they are logging
#    to. If the file changes, it is closed and reopened using the file
#    name. This handler is only useful on Unix-like systems; Windows
#    does not support the underlying mechanism used.
#
#14. "QueueHandler" instances send messages to a queue, such as
#    those implemented in the "queue" or "multiprocessing" modules.
#
#15. "NullHandler" instances do nothing with error messages. They
#    are used by library developers who want to use logging, but want
#    to avoid the 'No handlers could be found for logger XXX' message
#    which can be displayed if the library user has not configured
#    logging. See *Configuring Logging for a Library* for more
#    information.
