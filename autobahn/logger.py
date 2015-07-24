from __future__ import absolute_import


def make_logger(logger_type=None):
    if logger_type == "twisted":
        # If we've been asked for the Twisted logger, try and get the new one
        try:
            from twisted.logger import Logger
            return PassthroughLogger(Logger())
        except ImportError:
            pass

    from logging import getLogger
    return PassthroughLogger(getLogger())


class PassthroughLogger(object):
    """
    A logger that passes through to the stuff.
    """
    def __init__(self, logger):
        self.logger = logger

    def critical(self, frmt, **kwargs):
        return self.logger.critical(frmt, **kwargs)

    def error(self, frmt, **kwargs):
        return self.logger.error(frmt, **kwargs)

    def warn(self, frmt, **kwargs):
        return self.logger.warn(frmt, **kwargs)

    def info(self, frmt, **kwargs):
        return self.logger.info(frmt, **kwargs)

    def debug(self, frmt, **kwargs):
        return self.logger.debug(frmt, **kwargs)
