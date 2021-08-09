from datetime import datetime
from settings import LOG_LEVEL

class logger:

    def __init__(self):
        self.logLevel = {'DEBUG' : 5, 'INFO' : 4 , 'WARN' : 3, 'ERROR' : 2, 'CRITI' : 1}

    def log(self, severity, message):
        if self.logLevel[LOG_LEVEL] >= self.logLevel[severity]:
            print('[{}] | {} | {}'.format(severity, str(datetime.now()), message))

    def debug(self, message):
        self.log('DEBUG', message)

    def info(self, message):
        self.log('INFO', message)

    def warn(self, message):
        self.log('WARN', message)

    def error(self, message):
        self.log('ERROR', message)

    def critical(self, message):
        self.log('CRITI', message)

# log = logger()
# log.debug('Debug message')
# log.info('Info message')
# log.warn('Warning message')
# log.error('Error message')
# log.critical('Critical message')