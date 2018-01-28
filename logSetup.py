import logging


def setup_logger(name='root', format='[%(asctime)s] [%(threadName)s/%(levelname)s] %(message)s', dateformat='%H:%M:%S', level="INFO"):
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(format, datefmt=dateformat)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.getLevelName(level))
    return logger