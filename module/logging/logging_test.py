import logging
import logging.handlers as handlers


def logging_stream_test():
    #create logger
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.DEBUG)
    
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # add formatter to ch
    ch.setFormatter(formatter)
    
    # add ch to logger
    logger.addHandler(ch)
    
    # 'application' code 
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')

def logging_sococket():
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.DEBUG)
    
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    ch_soc = logging.H
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # add formatter to ch
    ch.setFormatter(formatter)
    
    # add ch to logger
    logger.addHandler(ch)
    
    # 'application' code 
    logger.debug('debug message')


LOG_BIND_PORT = 20001
LOG_SVR_HOST = '127.0.0.1'

class logging_client():
    def __init__(self):
       pass 
    def init(self, name, level, host, port, memoryCapacity):
        target = handlers.SocketHandler(host, port)
        if memoryCapacity > 0:
            hdlr = handlers.MemoryHandler(memoryCapacity,
                        logging.ERROR, target)
        else:
            hdlr = target
        hdlr.setLevel(level)
        logger = logging.getLogger(name)
        logger.addHandler(hdlr)
        logger.setLevel(level)
        return logger

#from SocketServer import ThreadingTCPServer, StreamRequestHandler
from socketserver import ThreadingTCPServer, StreamRequestHandler
import logging.config
import logging.handlers as lhandlers
import os
import struct
import cPickle

class LogRequestHandler(StreamRequestHandler):
    def handle(self):
        while 1:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
              unk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            # 使用SocketHandler发送过来的数据包，要使用解包成为LogRecord
            # 看SocketHandler文档
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

            def unPickle(self, data):
                return cPickle.loads(data)

            def handleLogRecord(self, record):
                logger = logging.getLogger(record.name)
                logger.handle(record)\

            def startLogSvr(bindAddress, requestHandler):
                svr = ThreadingTCPServer(bindAddress, requestHandler)
                svr.serve_forever()

            def addHandler(name, handler):
                logger = logging.getLogger(name)
                logger.addHandler(handler)

                fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
                handler.setFormatter(fmt)

                logger.setLevel(logging.NOTSET)

            def memoryWapper(handler, capacity):
                hdlr = lhandlers.MemoryHandler(capacity, target = handler)
                hdlr.setFormatter(handler.formatter)
                return handler

            def main_run():
                path, dirname = os.path, os.path.dirname
                pth = dirname((path.realpath(__file__)))
                filename = path.join(dirname(pth), 'log', 'logging.log')
                #    logging.config.fileConfig(pth + r'/logging.conf')

                # 最终写到文件中
                hdlr = lhandlers.RotatingFileHandler(filename,
                                 maxBytes = 1024,backupCount = 3)
                # 还可以一个memoryhandler，达到一定数据或是有ERROR级别再flush到硬盘
                hdlr = memoryWapper(hdlr, 1024)
                addHandler('core', hdlr)
                print('OK: logerserver running...')
                startLogSvr(('0.0.0.0', LOG_BIND_PORT), LogRequestHandler)

if __name__ == "__main__":      
    #client start
    test = logging_client()
    test.init("loger_tester", logging.DEBUG, LOG_SVR_HOST, LOG_BIND_PORT, 1024)



