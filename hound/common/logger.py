import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from hound.common import cfg

core_opts = [
    cfg.StrOpt('log_dir', default='/var/log/hound',
                help=('The log directory')),
    cfg.StrOpt('log_file', default='server.log',
                help=('The log file')),
    cfg.IntOpt('log_file_size', default=16*1024*1024,
                help=('The log file size')),
    cfg.IntOpt('log_file_count', default=5, 
                help=('The log file count to logging')),
    cfg.BoolOpt('debug', default=True,
                help=('enable debug or not')),
    cfg.StrOpt('log_formatter', default='[%(asctime)s] %(name)s: [%(filename)s: %(lineno)d]: %(levelname)-8s: %(message)s',
                help=('format log output')),
]

CONF = cfg.CONF
CONF.register_opts(core_opts)

class Logger(object):
    
    m_logger = None

    def __init__(self, project):
        self._log_dir = CONF.log_dir
        self._log_file = CONF.log_file
        self._log_file_size = CONF.log_file_size
        self._log_file_count = CONF.log_file_count

        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)

        log_file_name = os.path.join(self._log_dir, self._log_file)
        self._log_handler = RotatingFileHandler(log_file_name, maxBytes =
                self._log_file_size, backupCount = self._log_file_count)
        
        Logger.m_logger = logging.getLogger(project)
        self._log_handler.setFormatter(logging.Formatter(CONF.log_formatter))

        self._enable_debug = CONF.debug
        if self._enable_debug:
            self._log_handler.setLevel(logging.DEBUG)
            Logger.m_logger.setLevel(logging.DEBUG)

        Logger.m_logger.addHandler(self._log_handler)    
        

def get_logger(project):
    log = Logger(project)
    return log.m_logger


# if __name__ == '__main__':
#     LOG = get_logger('artisan')
#     LOG.info("hello world")

