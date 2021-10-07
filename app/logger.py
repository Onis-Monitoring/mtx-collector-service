import logging
import logging.config
import logging.handlers

def logger(name, logLevel):
    filename='mtx-exporter.log'
    logger = logging.getLogger(name)
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=200000, backupCount=2)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logLevel)
    ch = logging.StreamHandler()
    ch.setLevel(logLevel)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

def logger_intersite(name, logLevel):
    filename='mtx-exporter_intersite.log'
    logger = logging.getLogger(name)
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=20000, backupCount=0)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logLevel)
    ch = logging.StreamHandler()
    ch.setLevel(logLevel)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger