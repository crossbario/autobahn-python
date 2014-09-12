import logging, logging.config, os, shutil

class mylog:
    def __init__(self):
        self.log_level = logging.DEBUG
        self.logger = None
        return

    def set_level(self, level):
        self.log_level = level

    def get_logger(self):
        logger = logging.getLogger('mylog')
        logger.setLevel(self.log_level)
        handler = logging.StreamHandler()
        handler.setLevel(self.log_level)
        logger.addHandler(handler)
        self.logger = logger

        return self.logger
